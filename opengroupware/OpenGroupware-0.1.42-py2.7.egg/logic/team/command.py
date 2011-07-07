from coils.core import *

class TeamCommand(object):

    def set_membership(self):
        ''' According to the zOGI Spec:
               Team entities are entirely read-only prior to r879 (2007-12-19). As of r879 the membership of a
               team can be adjusted via putObject assuming the user has sufficient permissions. Members of the
               team must be specified in the "memberObjectIds" attribute as an array of objectIds. '''
        if 'memberObjectIds' in self.values:
            # TODO: Grant this right to members of the 'team creators' team.
            if self._ctx.is_admin:
                member_ids = self.values['memberObjectIds']
                if isinstance(member_ids, basestring):
                    member_ids = [x.strip() for x in member_ids.split(',')]
                if isinstance(member_ids, list):
                    member_ids = [ int(x) for x in self.values['memberObjectIds'] ]
                    for member in self.obj.members:
                        if member.object_id in member_ids:
                            member_ids.remove(member.object_id)
                        else:
                            # Delete assignment from team
                            self._ctx.db_session().delete(member)
                    for member_id in member_ids:
                        self._ctx.db_session().add(CompanyAssignment(self.obj.object_id, member_id))
                else:
                    raiseCoilsException('Team membership must be specified as a list of object ids')
