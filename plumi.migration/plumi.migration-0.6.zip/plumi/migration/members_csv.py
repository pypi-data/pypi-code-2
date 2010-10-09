import logging
import tempfile
import base64
import csv

from Products.CMFCore.utils import getToolByName
from OFS.Image import Image
from zope.component import getUtility  
from plumi.migration.interfaces.migration import IMemberMigrationConfiguration
from plumi.app.member_area import notifyMemberAreaCreated

NUMBER_OF_TOKENS = 17

def import_members_csv(context):
    log = logging.getLogger('plumi.migration')
    util = getUtility(IMemberMigrationConfiguration, name='member_migration_config', context=context)

    log.info("members_csv started with util %s. Its settings are : dry run ? %s delete members ? %s, len  of csv data %s" % (util, util.dry_run, util.delete_existing_members, len(util.members_csv_file)))
    
    #Write the csv data to a temporary file
    f = tempfile.NamedTemporaryFile()
    f.write(util.members_csv_file)
    f.flush()
    log.debug(' tempfile is %s ' % f.name)
 
    csv_file_lines = ''
    try:
        csv_file_lines = open(f.name,'r').read()
    except Exception, e:
        log.error('opening %s caused exception. exception is %s' % (f.name,e))
        return "Temporary file couldnt be opened."

    #parse the file to a csv reader
    reader = csv.reader(open(f.name,'r'),delimiter=';', quoting=csv.QUOTE_MINIMAL)

    regtool = getToolByName(context, 'portal_registration')
    portal_membership = getToolByName(context, 'portal_membership')
    membertool = getToolByName(context,'portal_memberdata')
    imported_count = 0

    index = 1
    for row in reader:
        #we want to skip the first 
        if not index == 1:
            log.debug(' using %s as user data ' % row )
            if len(row) == NUMBER_OF_TOKENS:
                member_id, passwd, fullname, email, location, home_page, description, city,street,postcode,phone,url,genre_interests,activities,media_formats,userbio,portrait = row
                if genre_interests == '':
                        genre_interests = []
                else: 
                        genre_interests = eval(genre_interests) 
                        #we need to capitalise the first letter of the genre interests - they have changed string literals
                        genre_interests_mod = []
                        for x in genre_interests:
                            genre_interests_mod.append(x[0].upper() + x[1:])
                        genre_interests = genre_interests_mod
                if activities == '':
                        activities = []
                else:
                        activities = eval(activities)
                if media_formats == '':
                        media_formats = []
                else:
                        media_formats = eval(media_formats)

                properties =  {
                        'username' : member_id,
                        'fullname' : fullname,
                        'email' : email.strip(),
                        'location': location,
                        'home_page' : home_page,
                        'description':description,
                        'city':city,
                        'street':street,
                        'postcode':postcode,
                        'phone':phone,
                        'url':url,
                        'genre_interests':genre_interests,
                        'activities':activities,
                        'media_formats':media_formats,
                        'userbio':userbio,
                            }
                try:
                    if util.delete_existing_members and not util.dry_run:
                        log.debug("deleting %s " % member_id)
                        portal_membership.deleteMembers(member_id)
                    #debug line to list our custom attribs
                    log.debug(" genre_interests, activities, media_formats %s %s %s " % (genre_interests, activities, media_formats))
                    if not util.dry_run:
                        regtool.addMember(member_id, passwd, properties=properties)
                        #decode the portrait data
                        img_data = base64.b64decode(portrait)
                        portrait_image = Image(id=member_id, file=img_data, title='')
                        membertool._setPortrait(portrait_image, member_id)
                        #simulate first time login 
                        portal_membership.createMemberArea(member_id, True)
                    log.debug("Successfully added %s (%s) with email %s" % (fullname, member_id, email))
                    imported_count += 1

                except ValueError, e:
                    log.error("Couldn't add %s\n Properties are %s\nUser data string %s\nError: %s" % (member_id, properties,row,e))
            else:
                #else tokens on line didnt equal NUMBER_OF_TOKENS
                log.error("Could not parse line %d because it had the following contents: '%s'" % (index, row))

        #count every user line
        index += 1
    #end of loop over users

    f.close()

    # log and return results
    result =  "Imported %d users from %d lines of CSV, with %s lines in error." % (imported_count, index, index-imported_count)
    log.info(result)
    return result

