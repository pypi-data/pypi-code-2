# Copyright (c) 2011, RED Interactive Agency
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import os
import re
import functools
import random
import boto
import boto.ec2

class EC2Selector():
    
    def __init__(self, access_key=None, secret_key=None, input_function=None):
        '''Accepts a prompt function that can be superseded by Test::Unit'''
        if input_function:
            self.prompt = input_function
        else:
            self.prompt = lambda(prompt): raw_input(prompt)
        if access_key:
            os.environ['AWS_ACCESS_KEY_ID'] = access_key
        if secret_key:
            os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
    
    def pick_an_option(self, choices):
        while True:
            print('Please pick one of the available options:')
            for index, value in enumerate(choices):
                print(' [%d] %s' % (index, value))
            choice = self.prompt('> ')
            try:
                choice = int(choice)
                if choice in range(len(choices)):
                    print('Option selected: %s' % choice)
                    return choice
            except ValueError:
                pass
    
    def _list_images(self, connection, filters=None):
        """
        Return a list of EC2 images available for the given connection that 
        pass the specified filters.
    
        :type connection: `EC2Connection`
        :param connection: The connection to get the list of images from
    
        :type filters: dict
        :param filters: Optional filters that can be used to limit the 
                        interactive search for an image. Filters are provided 
                        in the form of a dictionary consisting of filter names 
                        as the key and filter values as the value.  The set of 
                        allowable filter names is: ['name', 'owner_id', 
                        'virtualization_type', 'image_type', 'architecture', 
                        'name_contains', 'owner_id_contains', ...]
    
        :rtype: list
        :return: A list of :class:`boto.ec2.image.Image`
        """
        # Extract _contains filters to apply on the returned filtered set
        contains_filters = {}
        if filters:
            for key in filters.keys():
                contains_length = len('_contains')
                if key[-contains_length:] == '_contains':
                    contains_filters[key[:-contains_length]] = filters.pop(key)
        # Retrieve the filtered list, remove those with empty names
        images = connection.get_all_images(filters=filters)
        images = [i for i in images if i.name is not None]
        images = [i for i in images if i.state == 'available']
        # Filter contains_name applying contains to 'name' attribute, and so on
        for key, value in contains_filters.iteritems():
            images = [i for i in images if getattr(i, key) \
                and re.search(value, getattr(i, key))]
        return images
    
    def _filter_images(self, images):
        """
        Presents an interactive prompt to filter the list images based on their 
        attributes and returns a list with the same or less items.
    
        :type images: list
        :param images: A list of :class:`boto.ec2.image.Image`
    
        :rtype: list
        :return: A list of :class:`boto.ec2.image.Image`
        """
        attributes = ['name', 'owner_id', 'architecture', 'type', 
            'virtualization_type',]
        # TODO: add the option to specify _contains attributes
        attribute = attributes[self.pick_an_option(attributes)]
        values = list(set([getattr(i, attribute) for i in images]))
        value = values[self.pick_an_option(values)]
        return [i for i in images if getattr(i, attribute) == value]
    
    def needs_authentication(f):
        """Prompt user for AWS access and secret keys when not specified."""
        @functools.wraps(f)
        def auth_prompting_wrapper(*args, **kw):
            self = args[0]
            while not os.environ.get('AWS_ACCESS_KEY_ID'):
                os.environ['AWS_ACCESS_KEY_ID'] = self.prompt(
                    "Enter your AWS access key ID: ")
            while not os.environ.get('AWS_SECRET_ACCESS_KEY'):
                os.environ['AWS_SECRET_ACCESS_KEY'] = self.prompt(
                    "Enter your AWS secret access key: ")
            try:
                boto.ec2.EC2Connection()
                return f(*args, **kw)
            except boto.exception.NoAuthHandlerFound:
                print("Invalid AWS credentials. Try again.")
        return auth_prompting_wrapper

    @needs_authentication
    def select(self, region_id=None, image_id=None, ask=False, filters=None):
        """
        Return one available EC2 image, optionally presenting an interactive 
        prompt to select one from the list of AMI available to your account.

        :type region_id: string
        :param region_id: The ID of the region the wanted image belongs to

        :type image_id: string
        :param image_id: The ID of the wanted images

        :type ask: boolean
        :param ask: Should prompt for a specific image_id if not entered?

        :type filters: dict
        :param filters: Optional filters that can be used to limit the 
                        interactive search for an image. Filters are provided 
                        in the form of a dictionary consisting of filter names 
                        as the key and filter values as the value.  The set of 
                        allowable filter names is: ['name', 'owner_id', 
                        'virtualization_type', 'image_type', 'architecture', 
                        'name_contains', 'owner_id_contains', ...]

        :rtype: :class:`boto.ec2.image.Image`
        :return: The selected EC2 Image or None if no image was selected    
        """
        # Pick a region
        all_regions = boto.ec2.regions()
        try:
            region = [r for r in all_regions if r.name == region_id][0]
        except IndexError:
            print('%d regions available' % len(all_regions))
            region = all_regions[self.pick_an_option(
                [r.name for r in all_regions])]
        connection = region.connect()
        # Pick an image
        if ask and not image_id:
            image_id = self.prompt("Enter the ID of an image (e.g. 'ami-" +
                "9a8bf') or type RETURN to interactively select from a list: ")
        if image_id:
            try:
                return connection.get_image(image_id)
            except boto.exception.EC2ResponseError:
                print('Image not found, switching to interactive selector.')
        # Load the available images, applying the specified filters
        print(("Loading list of available EC2 images for %s with filters: " +
            "%s, might take a while...") % (region.name, filters))
        images = self._list_images(connection, filters=filters)
        while len(images) > 1:
            print('%d images available.' % len(images))
            images = self._filter_images(images)
        print("Image selected: %s" % images[0].name)
        return images[0]
