import datetime
from django.contrib.auth.models import User,Group
from django.core.management import call_command
from adminapp.models import UserRole,UserProfile,UserPrivilege





roles=['System Admin','Admin','Approver','Validator','Administration','Import PN33','Schedule','Dispatch','Upload','System User']
privileges=['Dashboard','Import PN33','Schedule','Dispatch','Validation1','Validation2','Approve schedule','Upload','System User','Administration']

def run():
    today = datetime.date.today()
    try:
        for privilege in privileges:
            try:
                g = UserPrivilege.objects.get(privilege=privilege)
            except UserPrivilege.DoesNotExist:
                userPrivilege = UserPrivilege(
                    privilege=privilege,
                    created_by='admin',
                    updated_by='admin',
                    created_date=today,
                    updated_date=today,
                    is_deleted=False,
                )
                userPrivilege.save()

        try:
            g = UserRole.objects.get(role="System Admin")
            print g.role
        except UserRole.DoesNotExist:
            userprivilege = UserPrivilege.objects.all()
            userrole = UserRole(
                role="System Admin",
                #privilege=userprivilege,
                created_by='admin',
                updated_by='admin',
                created_date=today,
                updated_date=today,
                is_deleted=False
            )
            userrole.save()
            for privilege in userprivilege:
                userrole.privilege.add(privilege)


        # userprivilege1=UserPrivilege.objects.filter().exclude(privilege='Administration')
        # userrole = UserRole(
        #     role="Admin",
        #     # privilege=userprivilege,
        #     created_by='admin',
        #     updated_by='admin',
        #     created_date=today,
        #     updated_date=today,
        #     is_deleted=False
        # )
        # print ""
        # userrole.save()
        # print "----------userrole---------", userrole
        # for userprivilege in userprivilege1:
        #     userrole.privilege.add(userprivilege)
        #
        #
        userprivilege2= UserPrivilege.objects.filter(privilege='Validation1')
        try:
            g = UserRole.objects.get(role="VALIDATOR_1")
        except UserRole.DoesNotExist:
            userrole = UserRole(
                role="VALIDATOR_1",
                # privilege=userprivilege,
                created_by='admin',
                updated_by='admin',
                created_date=today,
                updated_date=today,
                is_deleted=False
            )
            userrole.save()
            for userprivilege in userprivilege2:
                userrole.privilege.add(userprivilege)




        userprivilege3 = UserPrivilege.objects.filter(privilege='Validation2')
        try:
            g = UserRole.objects.get(role="VALIDATOR_2")
        except UserRole.DoesNotExist:
            userrole = UserRole(
                role="VALIDATOR_2",
                # privilege=userprivilege,
                created_by='admin',
                updated_by='admin',
                created_date=today,
                updated_date=today,
                is_deleted=False
            )
            userrole.save()
            for userprivilege in userprivilege3:
                userrole.privilege.add(userprivilege)
        #
        # userprivilege4 = UserPrivilege.objects.filter(privilege='Import PN33')
        # userrole = UserRole(
        #     role="Import PN33",
        #     # privilege=userprivilege,
        #     created_by='admin',
        #     updated_by='admin',
        #     created_date=today,
        #     updated_date=today,
        #     is_deleted=False
        # )
        #
        # userrole.save()
        # print "----------userrole---------", userrole
        # for userprivilege in userprivilege4:
        #     userrole.privilege.add(userprivilege)
        #
        # userprivilege5 = UserPrivilege.objects.filter(privilege='Dispatch')
        # userrole = UserRole(
        #     role="Dispatch",
        #     # privilege=userprivilege,
        #     created_by='admin',
        #     updated_by='admin',
        #     created_date=today,
        #     updated_date=today,
        #     is_deleted=False
        # )
        # print ""
        # userrole.save()
        # print "----------userrole---------", userrole
        # for userprivilege in userprivilege5:
        #     userrole.privilege.add(userprivilege)
        #
        # userprivilege6 = UserPrivilege.objects.filter(privilege='Schedule')
        # userrole = UserRole(
        #     role="Schedule",
        #     # privilege=userprivilege,
        #     created_by='admin',
        #     updated_by='admin',
        #     created_date=today,
        #     updated_date=today,
        #     is_deleted=False
        # )
        # print ""
        # userrole.save()
        # print "----------userrole---------", userrole
        # for userprivilege in userprivilege6:
        #     userrole.privilege.add(userprivilege)
        #
        userprivilege7 = UserPrivilege.objects.filter(privilege='Approve schedule')
        try:
            g = UserRole.objects.get(role="Approver")
        except UserRole.DoesNotExist:
            userrole = UserRole(
                role="Approver",
                # privilege=userprivilege,
                created_by='admin',
                updated_by='admin',
                created_date=today,
                updated_date=today,
                is_deleted=False
            )
            userrole.save()
            for userprivilege in userprivilege7:
                userrole.privilege.add(userprivilege)
        #
        # userprivilege8 = UserPrivilege.objects.filter(privilege='Upload B30')
        # userrole = UserRole(
        #     role="Upload B30",
        #     # privilege=userprivilege,
        #     created_by='admin',
        #     updated_by='admin',
        #     created_date=today,
        #     updated_date=today,
        #     is_deleted=False
        # )
        # userrole.save()
        # print "----------userrole---------",userrole
        # for userprivilege in userprivilege8:
        #     userrole.privilege.add(userprivilege)
        #
        # userprivilege9 = UserPrivilege.objects.filter(privilege='System User')
        # userrole = UserRole(
        #     role="System User",
        #     # privilege=userprivilege,
        #     created_by='admin',
        #     updated_by='admin',
        #     created_date=today,
        #     updated_date=today,
        #     is_deleted=False
        # )
        # userrole.save()
        # print "----------userrole---------", userrole
        # for userprivilege in userprivilege9:
        #     userrole.privilege.add(userprivilege)
        #
        # userprivilege10 = UserPrivilege.objects.filter(privilege='Administration')
        # userrole = UserRole(
        #     role="Administrator",
        #     # privilege=userprivilege,
        #     created_by='admin',
        #     updated_by='admin',
        #     created_date=today,
        #     updated_date=today,
        #     is_deleted=False
        # )
        # userrole.save()
        # print "----------userrole---------", userrole
        # for userprivilege in userprivilege10:
        #     userrole.privilege.add(userprivilege)



    except Exception, e:
        print 'Exception|role.py|array', e
    return



