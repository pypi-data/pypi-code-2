def main(self):
    """ Update Zope Groups """
    output = ""
    groups = self.portal_groups.listGroups()
    output = output + 'gruppi da analizzare: ' + str(len(groups)) + '\n'
    for group in groups:
        group_data = group.getGroup()
        processed = {}
        processed['title'] = group_data.getProperty('title')
        processed['description'] = group_data.getProperty('description')
        try:
            self.portal_groups.updateGroup(group.id,processed)
            output = output + 'Aggiornato gruppo ' + group.id + ' con i parametri:' + str(processed) + '\n'
        except KeyError:
            output = output + 'ERRORE: Gruppo non presente in Zope: ' +group.id  + '\n'
            pass
    return output