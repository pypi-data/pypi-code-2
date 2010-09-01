#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from sqlalchemy.orm import relation
from sqlalchemy     import and_, or_
from internal       import ACL, AuditEntry, ObjectLink, ObjectInfo, Team
from task           import Task, TaskAction
from company        import Address, Telephone, CompanyValue, CompanyInfo
from contact        import Contact
from enterprise     import Enterprise
from appointment    import Appointment, Resource, DateInfo, Participant
from doc            import Note, Document, Folder
from project        import Project
from assignment     import ProjectAssignment, CompanyAssignment
from collection     import Collection, CollectionAssignment
from route          import Route
from process        import Process
from property      import ObjectProperty
from message        import Message

Appointment.participants         = relation('Participant',
                                   lazy=True,
                                   uselist=True,
                                   cascade='delete',
                                   primaryjoin='Participant.appointment_id==Appointment.object_id')

Appointment.notes                = relation('Note',
                                   lazy=True,
                                   uselist=True,
                                   order_by='Note.company_id',
                                   primaryjoin='Note.appointment_id==Appointment.object_id')

Appointment.acls                 = relation('ACL',
                                   lazy=False,
                                   uselist=True,
                                   cascade='delete',
                                   order_by='ACL.context_id',
                                   primaryjoin='ACL.parent_id == Appointment.object_id')

Appointment.logs                 = relation('AuditEntry',
                                   lazy=True,
                                   uselist=True,
                                   order_by='AuditEntry.context_id',
                                   primaryjoin='Appointment.object_id==AuditEntry.context_id')

Appointment.properties           = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   cascade='delete',
                                   order_by='ObjectProperty.parent_id',
                                   primaryjoin='Appointment.object_id==ObjectProperty.parent_id')

#CollectionAssignment.collection  = relation('Collection',
#                                   uselist=False,
#                                   primaryjoin='Collection.collection_id==CollectionAssignment.collection_id')

#Collection.project                = relation('Project',
#                                    uselist=False,
#                                    primaryjoin='Collection.project_id==Project.object_id')

#Collection.acls                   = relation('ACL',
#                                    lazy=False,
#                                    uselist=True,
#                                    order_by='ACL.context_id',
#                                    primaryjoin='ACL.parent_id == Collection.object_id')

#Collection.members                = relation('CollectionAssignment',
#                                    lazy=True,
#                                    uselist=True,
#                                    order_by='CollectionAssignment.object_id',
#                                    primaryjoin='CollectionAssignment.collection_id == Collection.object_id')

#Collection.logs                   = relation('AuditEntry',
#                                    lazy=True,
#                                    uselist=True,
#                                    order_by='AuditEntry.context_id',
#                                    primaryjoin='Collection.object_id==AuditEntry.context_id')

Contact.addresses                 = relation('Address',
                                    cascade='delete',
                                    lazy=True,
                                    uselist=True,
                                    order_by='Address.kind',
                                    primaryjoin='Address.parent_id==Contact.object_id')

Contact.telephones                = relation('Telephone',
                                    cascade='delete',
                                    lazy=True,
                                    uselist=True,
                                    order_by='Telephone.kind',
                                    primaryjoin='Telephone.parent_id==Contact.object_id')

Contact.company_values            = relation('CompanyValue',
                                    lazy=True,
                                    cascade='delete',
                                    uselist=True,
                                    order_by='CompanyValue.name',
                                    primaryjoin='CompanyValue.parent_id==Contact.object_id')

Contact.notes                     = relation('Note',
                                    lazy=True,
                                    uselist=True,
                                    order_by='Note.company_id',
                                    primaryjoin='Note.company_id==Contact.object_id')

Contact.acls                      = relation('ACL',
                                    lazy=False,
                                    uselist=True,
                                    order_by='ACL.context_id',
                                    cascade='delete',
                                    primaryjoin='ACL.parent_id == Contact.object_id')

Contact.enterprises               = relation('CompanyAssignment',
                                    lazy=True,
                                    cascade='delete',
                                    uselist=True,
                                    order_by='CompanyAssignment.child_id',
                                    primaryjoin='CompanyAssignment.child_id == Contact.object_id')

Contact.teams                     = relation('CompanyAssignment',
                                    lazy=True,
                                    cascade='delete',
                                    uselist=True,
                                    order_by='CompanyAssignment.child_id',
                                    primaryjoin='CompanyAssignment.child_id == Contact.object_id')

Contact.projects                  = relation('ProjectAssignment',
                                    lazy=True,
                                    cascade='delete',
                                    uselist=True,
                                    order_by='ProjectAssignment.child_id',
                                    primaryjoin='Contact.object_id==ProjectAssignment.child_id')

Contact.logs                      = relation('AuditEntry',
                                    lazy=True,
                                    cascade='delete',
                                    uselist=True,
                                    order_by='AuditEntry.context_id',
                                    primaryjoin='Contact.object_id==AuditEntry.context_id')

Contact.properties               = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   order_by='ObjectProperty.parent_id',
                                   cascade='delete',
                                   primaryjoin='Contact.object_id==ObjectProperty.parent_id')

CompanyValue.properties          = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   order_by='ObjectProperty.parent_id',
                                   cascade='delete',
                                   primaryjoin='CompanyValue.object_id==ObjectProperty.parent_id')

Note.appointment                  = relation('Appointment',
                                    uselist=False,
                                    primaryjoin='Note.object_id==Appointment.object_id')

Note.project                      = relation('Project',
                                    uselist=False,
                                    primaryjoin='Note.project_id==Project.object_id')

Document.project                  = relation('Project',
                                    uselist=False,
                                    primaryjoin='Document.project_id==Project.object_id')

Document.folder                   = relation('Folder',
                                    uselist=False,
                                    primaryjoin='Document.folder_id==Folder.object_id')

Document.versions                 = relation('DocumentVersion',
                                             lazy=True,
                                             uselist=True,
                                             order_by='DocumentVersion.version',
                                             primaryjoin='Document.object_id==DocumentVersion.document_id')

Folder.project                    = relation('Project',
                                    uselist=False,
                                    primaryjoin='Document.project_id==Project.object_id')

Folder.folder                     = relation('Folder',
                                    uselist=False,
                                    primaryjoin='Folder.folder_id==Folder.object_id')

Enterprise.addresses              = relation('Address',
                                    uselist=True,
                                    cascade='delete',
                                    order_by='Address.kind',
                                    primaryjoin='Address.parent_id==Enterprise.object_id')

Enterprise.telephones             = relation('Telephone',
                                    uselist=True,
                                    cascade='delete',
                                    order_by='Telephone.kind',
                                    primaryjoin='Telephone.parent_id==Enterprise.object_id')

Enterprise.company_values         = relation('CompanyValue',
                                    uselist=True,
                                    order_by='CompanyValue.name',
                                    primaryjoin='CompanyValue.parent_id==Enterprise.object_id')

Enterprise.notes                  = relation('Note',
                                    uselist=True,
                                    order_by='Note.company_id',
                                    primaryjoin='Note.company_id==Enterprise.object_id')

Enterprise.contacts               = relation('CompanyAssignment',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='CompanyAssignment.parent_id',
                                    primaryjoin='CompanyAssignment.parent_id == Enterprise.object_id')

Enterprise.projects               = relation('ProjectAssignment',
                                    uselist=True,
                                    lazy=True,
                                    order_by='ProjectAssignment.child_id',
                                    primaryjoin='ProjectAssignment.child_id == Enterprise.object_id')

Enterprise.logs                   = relation('AuditEntry',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='AuditEntry.context_id',
                                    primaryjoin='Enterprise.object_id==AuditEntry.context_id')

Enterprise.acls                   = relation('ACL',
                                    uselist=True,
                                    lazy=False,
                                    cascade='delete',
                                    order_by='ACL.context_id',
                                    primaryjoin='ACL.parent_id == Enterprise.object_id')

Enterprise.properties            = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   cascade='delete',
                                   order_by='ObjectProperty.parent_id',
                                   primaryjoin='Enterprise.object_id==ObjectProperty.parent_id')

Team.members                      = relation('CompanyAssignment',
                                    lazy=False,
                                    uselist=True,
                                    order_by='CompanyAssignment.child_id',
                                    primaryjoin=('CompanyAssignment.parent_id == Team.object_id'))

Project.folder                    = relation('Folder',
                                    lazy=False,
                                    uselist=False,
                                    primaryjoin=and_(Project.object_id==Folder.project_id,
                                                     or_(Folder.folder_id == None,
                                                         Folder.folder_id == 0)))

Project.tasks                     = relation('Task',
                                    uselist=True,
                                    primaryjoin=(Project.object_id==Task.project_id))

Project.assignments               = relation(ProjectAssignment,
                                    uselist=True,
                                    cascade='delete',
                                    primaryjoin=(Project.object_id==ProjectAssignment.parent_id))

Project.properties                = relation('ObjectProperty',
                                    lazy=True,
                                    uselist=True,
                                    order_by='ObjectProperty.parent_id',
                                    cascade='delete',
                                    primaryjoin='Project.object_id==ObjectProperty.parent_id')

Route.acls                        = relation('ACL',
                                    lazy=False,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='ACL.context_id',
                                    primaryjoin='ACL.parent_id == Route.object_id')

Route.logs                        = relation('AuditEntry',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='AuditEntry.context_id',
                                    primaryjoin='Route.object_id==AuditEntry.context_id')

Route.properties                  = relation('ObjectProperty',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='ObjectProperty.parent_id',
                                    primaryjoin='Route.object_id==ObjectProperty.parent_id')

Process.route                     = relation('Route',
                                    lazy=True,
                                    uselist=False,
                                    order_by='Route.object_id',
                                    primaryjoin='Process.route_id==Route.object_id')

Process.properties                = relation('ObjectProperty',
                                    lazy=True,
                                    uselist=True,
                                    order_by='ObjectProperty.parent_id',
                                    cascade='delete',
                                    primaryjoin='Process.object_id==ObjectProperty.parent_id')

Route.processes                   = relation('Process',
                                    lazy=True,
                                    uselist=True,
                                    order_by='Process.object_id',
                                    primaryjoin='Route.object_id==Process.route_id')

Task.notes                        = relation(TaskAction,
                                    lazy=False,
                                    uselist=True,
                                    cascade='delete',
                                    order_by=TaskAction.action_date,
                                    primaryjoin=Task.object_id==TaskAction.task_id)

Task.owner                        = relation('Contact',
                                    uselist=False,
                                    primaryjoin='Task.owner_id==Contact.object_id')

Task.project                      = relation('Project',
                                    uselist=False,
                                    primaryjoin='Task.project_id==Project.object_id')

Task.project_assignments          = relation('ProjectAssignment',
                                    uselist=True,
                                    primaryjoin='Task.project_id==ProjectAssignment.parent_id')


Task.creator                      = relation('Contact',
                                    uselist=False,
                                    primaryjoin='Task.creator_id==Contact.object_id')

Task.logs                         = relation('AuditEntry',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='AuditEntry.context_id',
                                    primaryjoin='Task.object_id==AuditEntry.context_id')

Task.acls                         = relation(ACL,
                                    lazy=False,
                                    uselist=True,
                                    cascade='delete',
                                    order_by=ACL.context_id,
                                    primaryjoin=ACL.parent_id==Task.object_id)

TaskAction.task                   = relation('Task',
                                    uselist=False,
                                    primaryjoin='TaskAction.job_id==Task.object_id')

TaskAction.actor                 = relation('Contact',
                                    uselist=False,
                                    primaryjoin='TaskAction.actor_id==Contact.object_id')

Task.properties                   = relation('ObjectProperty',
                                    lazy=True,
                                    uselist=True,
                                    order_by='ObjectProperty.parent_id',
                                    cascade='delete',
                                    primaryjoin='Task.object_id==ObjectProperty.parent_id')

ProjectAssignment.project         = relation(Project,
                                    uselist=False,
                                    primaryjoin=(ProjectAssignment.parent_id==Project.object_id))