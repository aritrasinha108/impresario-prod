from django.shortcuts import render, redirect
from .models import Organization, MembershipLevel
from django.contrib.auth.models import User
from accounts.models import Account
from django.db.models import Max


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



