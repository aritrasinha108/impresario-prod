from django.shortcuts import render, redirect
from .models import Organization, MembershipLevel, TeamRequest
from django.contrib.auth.models import User
from accounts.models import Account
from django.db.models import Max
from django.http import JsonResponse


def create_org(request):
    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            name = request.POST['name']
            members = request.POST.getlist('checks')
            user = request.user
            description = request.POST['description']
            if Organization.objects.filter(name=name,parent_org__id=None).exists():
                warning = "Team with this name already exists"
            else:
                org = Organization.objects.create(
                    name=name,
                    parent_org_id=None
                )
                members = User.objects.filter(pk__in=members)
                MembershipLevel.create_team(members, org, None, request.user.id)
                warning = "Team created"
                return redirect('home')
        memberships = Account.objects.all()
        return render(request, 'create_team.html', {
            'memberships': memberships,
            'warning': warning,
            'user': request.user
        })
    else:
        return redirect('accounts:login')


def org_tree(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    queryset_roles = MembershipLevel.objects.filter(user__username=request.user.username)
    queryset = Organization.objects.all()
    mq = queryset_roles.aggregate(Max('organization__id'))
    if mq['organization__id__max'] is None:
        adj = [[] for i in range(len(queryset_roles) + 1)]
    else:
        adj = [[] for i in range(mq['organization__id__max'] + 1)]
    name_dict = {}
    for i in queryset_roles:
        org = i.organization.id
        role = MembershipLevel.objects.get(user=i.user.id, organization__id=org).role
        j = Organization.objects.get(pk=org)
        if(role == 1):
            child_org = Organization.objects.filter(parent_org=i.organization.id)
            for child in child_org:
                adj[i.organization.id].append(child.id)
                name_dict[child.id] = child.name
        while(j.parent_org_id is not None):
            if(j.id in adj[j.parent_org_id]):
                j = Organization.objects.get(pk=j.parent_org_id)
            else:
                adj[j.parent_org_id].append(j.id)
                name_dict[j.parent_org_id] = j.parent_org.name
                name_dict[j.id] = j.name
                j = Organization.objects.get(pk=j.parent_org_id)
        if(j.id in adj[0]):
            continue
        else:
            adj[0].append(j.id)
            name_dict[j.id] = j.name
    # Making listo
    listo = []
    make_listo(0, adj, name_dict, 0, listo)
    # Printing adjacency oganisation tree of user's organisations
    print("\nadjacency list:")
    for i in range(len(adj)):
        print("\n", i, ": ", end=" ")
        for j in adj[i]:
            print(j, end=" ")
    return render(request, 'org_tree.html', {
        'listo': listo,
        'user': request.user
    })

# Makes a list to be passed in the context to org_tree.html
def make_listo(node, adj, name_dict, depth, listo):
    for i in adj[node]:
        listo.append([name_dict[i], depth, i])
        make_listo(i, adj, name_dict, depth + 8, listo)


def org_detail(request, org_id):
    org =  Organization.objects.get(pk=org_id)
    child_org = Organization.objects.filter(parent_org=org_id)
    members = MembershipLevel.objects.filter(organization=org)
    role = MembershipLevel.objects.get(organization__id=org_id, user_id=request.user.id).role
    return render(request, 'org_detail.html', {
        'child_org': child_org,
        'org': org,
        'par_id': org_id,
        'members': members,
        'user': request.user,
        'role': role
    })


def create_team(request, par_id) :
    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            team_name = request.POST['name']
            members = request.POST.getlist('checks')
            user = request.user
            description = request.POST['description']
            if Organization.objects.filter(name = team_name,parent_org__id = par_id).exists():
                warning = "Team with that name already exists"
            elif MembershipLevel.objects.get(user_id=request.user.id, organization_id=par_id).role == 1 : # If user is an admin
                org = Organization.objects.create(
                    name=team_name,
                    parent_org_id=par_id,
                    description=description
                )
                members = User.objects.filter(pk__in=members)
                MembershipLevel.create_team(members, org,par_id, request.user.id)
                warning = "Team created"
                return redirect('organisations:org_tree')
            else :
                TeamRequest.create_team_req(
                    user,
                    team_name,
                    description,
                    par_id,
                    members
                ) # If user is a participant
                warning = "Team request sent to admin"
        memberships = MembershipLevel.objects.filter(organization__id=par_id)
        return render(request, 'create_team.html', {
            'memberships': memberships,
            'warning': warning,
            'user': request.user
        })
    else:
        return redirect('accounts:login')


# Function used for retrieving ids of child organisations
def retrieve_child_org(parent, child):
    count = Organization.objects.filter(parent_org=parent).count()
    if count != 0:
        child_org = Organization.objects.filter(parent_org=parent)
        for i in child_org:
            retrieve_child_org(i.id, child)
            child.append(i.id)

def remove_team(member_id,org_id):     
    flag = False
    par_id = Organization.objects.get(pk=org_id).parent_org_id
    while par_id is not None:
        role = MembershipLevel.objects.get(user_id = member_id, organization__id = par_id).role
        if role == 1:
            flag = True
            break
        par_id = Organization.objects.get(pk=par_id).parent_org
    if flag == False:
        # Retrievig child organisations and storing their ids in child[]
        child = []
        retrieve_child_org(org_id, child)
        child.append(org_id)
        for org in child:
            # Checking whether the user is a part of the organization
            if MembershipLevel.objects.filter(organization__id=org, user_id=member_id).exists():
                role = MembershipLevel.objects.get(organization__id=org, user_id=member_id).role
                p = User.objects.get(pk=member_id)
                total_members = MembershipLevel.objects.filter(organization__id=org).count()
                if total_members > 1:
                    # If the person is admin
                    if role == 1:
                        admin = MembershipLevel.objects.filter(organization__id=org, role=1).count()
                        # If count of admin > 1 then he will easily leave the team
                        if admin > 1:
                            MembershipLevel.leave_team(p, org)
                        else: # If count of admin is one then before leaving some random person should be made as admin
                            members = MembershipLevel.objects.filter(organization__id=org)
                            # Accessing the member of team which was first added to team. 
                            user = MembershipLevel.random_fun(members, org, member_id)
                            q = User.objects.filter(pk=user)
                            # Making random person admin
                            MembershipLevel.change_role(q, org)
                            # Admin leaving the team
                            MembershipLevel.leave_team(p, org)
                    else:
                        # If the person is participant
                        MembershipLevel.leave_team(p, org)
                else: 
                    MembershipLevel.leave_team(p, org)
                    Organization.delete_org(org)

def edit_team(request, org_id) :
    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            name = request.POST['name']
            description = request.POST['description']
            new_members = request.POST.getlist('checks')
            old_team_name = Organization.objects.get(pk=org_id).name
            par_id = Organization.objects.get(pk = org_id).parent_org_id
            Organization.update_team(old_team_name, name, description, par_id)
            ex_members = MembershipLevel.objects.filter(organization__id=org_id)
            ids = []
            for i in ex_members:
                ids.append(i.user_id)
            ex_members = User.objects.filter(pk__in=ids)
            new_members = User.objects.filter(pk__in=new_members)
            for member in ex_members:
                if member not in new_members:
                    remove_team(member.id, org_id)           
            MembershipLevel.edit_team(ex_members, new_members, org_id, par_id, request.user.id)
            warning = "Editing successful"
        par_id = Organization.objects.get(pk=org_id).parent_org_id
        if par_id is None:
            memberships = Account.objects.all()
        else:
            memberships = MembershipLevel.objects.filter(organization__id=par_id)
        organisation = Organization.objects.get(pk=org_id)    
        return render(request, 'edit_team.html', {
            'memberships': memberships,
            'org': organisation,
            'warning': warning,
            'user': request.user
        })
    else:
        return redirect('accounts:login')


def team_reqs(request, par_id) :
    if request.user.is_authenticated:
        user = request.user
        top_org = Organization.get_top_org(par_id)
        all_sub_org = Organization.get_all_children(top_org)
        sub_org = MembershipLevel.get_subgroups(all_sub_org, user)
        tr_request = TeamRequest.objects.filter(par_org__in=sub_org, status = 2) 
        return render(request, 'team_requests.html', {
            'team_request': tr_request,
            'user': request.user
        })
    else:
        return redirect('accounts:login')


def ajax_change_status(request):
    if request.user.is_authenticated:
        request_status = request.GET.get('request_status', 2)
        request_id = request.GET.get('request_id', False)
        team_request = TeamRequest.objects.get(pk=request_id)
        try:
            request_status = int(request_status)
            if team_request.status == 1 :
                return JsonResponse({
                    'success': True,
                    'status': "Already approved"
                })
            elif team_request.status == 0 :
                return JsonResponse({
                    'success': True,
                    'status': "Already rejected"
                })
            elif request_status == 1:
                org = Organization.objects.create(name=team_request.team_name, parent_org_id=team_request.par_org.id)
                MembershipLevel.create_team(team_request.team_members.all(), org, team_request.par_org, team_request.sender.id)
                team_request.status = 1
                team_request.save()
                return JsonResponse({
                    'success': True,
                    'status': "Approved"
                })
            elif request_status == 0:
                team_request.status = 0
                team_request.save()
                return JsonResponse({
                    'success': True,
                    'status': "Rejected"
                }) 
        except Exception as e:
            return JsonResponse({
                'success': False
            })
    else:
        return redirect('accounts:login')


def change_role(request, org_id):
    if request.user.is_authenticated:
        warning = ''
        if request.method == 'POST':
            members = request.POST.getlist('checks')
            members = User.objects.filter(pk__in=members)
            MembershipLevel.change_role(members, org_id)
            warning = "Role changed to admin"
        memberships = MembershipLevel.objects.filter(organization__id=org_id, role=2)
        return render(request, 'change_role.html', {
            'memberships': memberships,
            'warning': warning,
            'user': request.user
        })
    else:
        return redirect('accounts:login')


def dismiss_admin(request, org_id):
    if request.user.is_authenticated:
        warning = ''
        admin = MembershipLevel.objects.filter(organization__id=org_id, role=1).count()
        if request.method == 'POST':
            members = request.POST.getlist('checks')
            count = len(members)
            if count == admin:
                warning = "Can't turn into participant"
            else:
                members = User.objects.filter(pk__in=members)
                MembershipLevel.change_role_participant(members, org_id)
                warning = "Role changed to participant"
        memberships = MembershipLevel.objects.filter(organization__id=org_id, role=1)
        return render(request, 'participant.html', {
            'memberships': memberships,
            'warning': warning,
            'user': request.user
        })
    else:
        return redirect('accounts:login')
        

def leave_team(request, org_id):
    if request.user.is_authenticated:
        warning=''     
        flag = False
        par_id = Organization.objects.get(pk=org_id).parent_org_id
        name = Organization.objects.get(pk=org_id).name
        while par_id is not None:
            role = MembershipLevel.objects.get(user_id=request.user.id, organization__id=par_id).role
            if role == 1:
                flag = True
                break
            par_id = Organization.objects.get(pk=par_id).parent_org
        if flag == True:
            warning = "Can't leave the team"
        else:
            # Retrievig child organisations and storing their ids in child[]
            child = []
            retrieve_child_org(org_id, child)
            child.append(org_id)
            for org in child:
                # Checking whether the user is a part of the organization
                if MembershipLevel.objects.filter(organization__id=org, user_id=request.user.id).exists():
                    role = MembershipLevel.objects.get(organization__id=org, user_id=request.user.id).role
                    p = User.objects.get(pk=request.user.id)
                    total_members = MembershipLevel.objects.filter(organization__id=org).count()
                    if total_members > 1:
                        # If the person is admin
                        if role == 1:
                            admin = MembershipLevel.objects.filter(organization__id=org, role=1).count()
                            # If count of admin > 1 then he will easily leave the team
                            if admin > 1:
                                MembershipLevel.leave_team(p, org)
                                warning = "Left the team"
                            else: # If count of admin is one then before leaving some random person should be made as admin
                                members = MembershipLevel.objects.filter(organization__id=org)
                                # Accessing the member of team which was first added to team. 
                                user = MembershipLevel.random_fun(members, org, request.user.id)
                                q = User.objects.filter(pk=user)
                                # Making random person admin
                                MembershipLevel.change_role(q, org)
                                # Admin leaving the team
                                MembershipLevel.leave_team(p, org)
                                warning = "Left the team"
                        else:
                            # If the person is participant
                            MembershipLevel.leave_team(p, org)
                            warning = "Left the team"
                    else: 
                        MembershipLevel.leave_team(p, org)
                        Organization.delete_org(org)
                        warning = "Left the team"
        return render(request, 'leave_team.html', {
            'warning': warning,
            'user': request.user,
            'name': name
        })
    else:
        return redirect('accounts:login')



