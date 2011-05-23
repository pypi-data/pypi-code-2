
from coils.core          import CoilsException, fix_microsoft_text
from api                 import BEBAPI

def render_address(context, entity, kind):
    response = { }
    for address in entity.addresses:
        if address.kind == kind:
            response['kind']       = kind
            response['name1']      = address.name1
            response['name2']      = address.name2
            response['name3']      = address.name3
            response['district']   = address.district
            response['street']     = address.street
            response['city']       = address.city
            response['province']   = address.province
            response['postalcode'] = address.postal_code
            response['country']    = address.country
            break
    else:
        response['kind']       = kind
        response['name1']      = ''
        response['name2']      = ''
        response['name3']      = ''
        response['district']   = ''
        response['street']     = ''
        response['city']       = ''
        response['province']   = ''
        response['postalcode'] = ''
        response['country']
    return response


def render_contact(context, contact):
    response = { 'objectid': contact.object_id,
                 'firstname': contact.first_name,
                 'lastname': contact.last_name,
                 'displayname': contact.get_display_name(),
                 'title': contact.get_company_value_text('job_title'),
                 'email': contact.get_company_value_text('email1'),
                 'telephone': { }
               }
    response['address'] = render_address(context, contact, 'mailing')
    for telephone in contact.telephones:
        if (telephone.kind == '01_tel'): key = 'main'
        elif (telephone.kind == '10_fax') : key = 'fax'
        elif (telephone.kind == '03_tel_func') : key = 'mobile'
        else: continue
        response['telephone'][key] = {'number': telephone.number, 'info': telephone.info }
    return response


def render_enterprise(context, enterprise, contacts):
    response = { 'objectid':  enterprise.object_id,
                 'name':      enterprise.name,
                 'bankcode':  enterprise.bank_code,
                 'address':   { },
                 'telephone': { },
                 'contacts':  [ ]
               }
    response['address'] = render_address(context, enterprise, 'ship')
    for telephone in enterprise.telephones:
        if (telephone.kind == '01_tel'): key = 'main'
        elif (telephone.kind == '10_fax') : key = 'fax'
        else: continue
        response['telephone'][key] = {'number': telephone.number, 'info': telephone.info }
    for contact in contacts:
        response['contacts'].append(render_contact(context, contact))
    return response


class CustomerAPI(BEBAPI):

    def api_customer_search(self, args):
        if (len(args)) and (isinstance(args[0], dict)):
            values = args[0]
            if (len(args) == 2):
                context_ids = self.translate_context_specification(args[1])
            else:
                context_ids = self.context.context_ids
            criteria = [ ]
            for key in args[0]:
                if (key in ('name', 'city', 'name1', 'street')):
                    value = fix_microsoft_text(args[0][key])
                    value = '%{0}%'.format(value.strip().lower())
                    if (key == 'city'): key = 'address.city'
                    elif (key=='name1'): key = 'address.name1'
                    elif (key=='street'): key = 'address.street'
                    criteria.append( { 'key': key,
                                       'value': value,
                                       'expression': 'ILIKE',
                                       'conjunction': 'OR' } )
            if (len(criteria) > 0):
                enterprises = self.context.run_command('enterprise::search', criteria=criteria,
                                                                             contexts=context_ids,
                                                                             limit = 50)
                contacts    = self.context.run_command('enterprise::get-contacts', enterprises=enterprises)
                response = [ render_enterprise(self.context, e, contacts[e.object_id]) for e in enterprises ]
                return response
        raise CoilsException('No criteria specified for search')
