
from urllib2 import Request, urlopen, HTTPError
#from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler
#from urllib2 import build_opener, install_opener
import base64
from datetime import datetime, timedelta

from lxml import etree
from lxml import objectify
from lxml.etree import tostring

import version

__all__ = [
    'game', 'open_games', 'all_users', 'user', 'latest_maps', 'headquarter',
    'game_state', 'map_layout', 'finish_turn', 'accept_invitation', 
    'decline_invitation', 'send_reminder', 'surrender_game', 'abandon_game',
    'chat', 'build_unit', 'unit_move_options', 'unit_attack_options', 
    'move_unit', 'attack_with', 'capture_base', 'repair_unit',
    'AuthenticationError', 'ServerError', 
    'UserNotFound', 'GameNotFound', 'MapNotFound', 
]

__version__ = version.VERSION

class ReadOnlyAPI (object):
    
    """
    Read-only API 
    =============
    
    This API provides basic information on users and games. It supports basic
    HTTP authentication for API calls to the Weewar REST service.

    A basic call for accessing your headquerter looks like this::

        >>> api = ReadOnlyAPI('eviltwin', '...')
        >>> no_games_needing_attentiont, game_data = api.headquarter()
        >>> print game_data
        [{'map': 1, 'rated': True, 'name': 'Twins, Basil!', 'state': 'finished', 
        'inNeedOfAttention': False, 'link': 'http://weewar.com/game/18682', ...

    """

    REQUESTS_PER_SECOND = 2 #: max requests per second

    def __init__(self, username=None, apikey=None):
        """
        Initialise API (with user credentials for authenticated calls).
        @param username: weewar username
        @type username: str
        @param apikey: Matching API key (from http://weewar.com/apiToken)
        @type apikey: str
        """
        self.username = username
        self.apikey = apikey

        #if username is not None:
        #    manager = HTTPPasswordMgrWithDefaultRealm()
        #    manager.add_password('users', 'weewar.com', username, apikey)
        #    opener = build_opener(HTTPBasicAuthHandler(manager))
        #    opener.addheaders = [
        #        ('Content-Type', 'application/xml'), 
        #        ('Accept', 'application/xml')
        #    ]
        #    install_opener(opener)
        
        self.last_call = datetime(1970, 1, 1)
        self.throttle = timedelta(seconds=1)/self.REQUESTS_PER_SECOND

    def _call_api(self, url, authentication=False, data=None):
        """
        Calls the weewar API with authentication (if specified)
        """
        headers = {
            'Content-Type' : 'application/xml',
            'Accept' : 'application/xml',
            'User-Agent' : 'python-weewar/%s' % __version__, 
        }

        if authentication and self.username is not None:
            base64string = base64.encodestring(
                '%s:%s' % (self.username, self.apikey))[:-1]
            headers['Authorization'] = 'Basic %s' % base64string

        # Be nice and wait for some time 
        # before submitting the next request
        while (datetime.now() - self.last_call) < self.throttle: 
            pass # Wait for it!
        self.last_call = datetime.now()

        #print 'opening %s...' % url
        #print headers
        req = Request(url, data, headers)

        try:
            handle = urlopen(req)
            return objectify.parse(handle).getroot()
            #xml = handle.read()
            #print xml
            #return objectify.fromstring(xml)
        except HTTPError, e:
            # HTTP response 401: Unauthorized
            if e.code == 401: 
                raise AuthenticationError
            elif e.code == 500:
                raise ServerError(e.msg)
            # otherwise raise again
            else: 
                raise

    def _parse_attrs(self, node, **attrs):
        """
        Parse node attributes and convert values into specified types.
        A typical call of this method would look like this::
        
            >>> from lxml import objectify
            >>> xml = '<terrain x="7" y="6" type="Base" finished="false" />'
            >>> node = objectify.fromstring(xml)
            >>> print _parse_attrs(node, x=int, y=int, type=str, finished=bool)
            {'x' : 7, 'y' : 6, 'type' : 'Base', 'finished' : False}
        
        Only attributes that are both specified in C{attrs} and turn up in the
        XML will end up in the resulting dict. Only exception here are boolean
        values which will default to C{False} if not found in the XML. 
        """
        values = {}
        for key, type_ in attrs.items():
            val = node.get(key, None)
            if val is not None or type_ is bool:
                if type_ is bool:
                    values[key] = str(val).lower().strip() == 'true'
                else:
                    try:
                        values[key] = type_(val)
                    except (ValueError, TypeError):
                        values[key] = val
        return values

    # Access specific games
    URL_GAME = 'http://weewar.com/api1/game/%s'

    def game(self, id):
        """
        Returns the status of a game and gives information about the
        participating players.
        """
        try:
            root = self._call_api(self.URL_GAME % id)
            return self._parse_game(root)
        except HTTPError, e:
            if e.code==404:
                raise GameNotFound(id)
            else:
                raise

    # Access all open games
    URL_OPEN_GAMES = 'http://weewar.com/api1/games/open'

    def open_games(self):
        """
        Returns all currently available open games.
        """
        # <games>
        #   <game id="181887" />
        #   ...
        # </games>
        root = self._call_api(self.URL_OPEN_GAMES)
        return [int(child.get('id'))
                for child in root.findall('game')]

    # Access a list of users
    URL_ALL_USERS = 'http://weewar.com/api1/users/all'

    def all_users(self):
        """
        Returns a list of all users who have been online in the last 7 days,
        including their current ranking.
        """
        root = self._call_api(self.URL_ALL_USERS)
        # <users>
        #   <user name="wulendam" id="21149" rating="1416" />
        #   ...
        # </users>
        return map(lambda node: self._parse_attrs(node, id=int, 
            name=str, rating=int), root.findall('user'))

    # Access a single user
    URL_USER = 'http://weewar.com/api1/user/%s'

    def user(self, username):
        """
        Returns detailed information about a single user, including everything
        that is visible on the profile page and the games the user is
        participating in.
        """
        try:
            root = self._call_api(self.URL_USER % username)
            return self._parse_user(root)
        except HTTPError, e:
            if e.code==404:
                raise UserNotFound(username)
            else:
                raise

    # Access the latest maps
    URL_LATEST_MAPS = 'http://weewar.com/api1/maps'

    def latest_maps(self):
        """
        Returns the latest published maps including urls for previews, images,
        and other details.
        """
        root = self._call_api(self.URL_LATEST_MAPS)
        return map(self._parse_map, root.findall('map'))

    # Access your headquarters
    URL_HEADQUARTER = 'http://weewar.com/api1/headquarters'

    def headquarter(self):
        """
        Returns all games that are listed in your Headquarters. Includes
        information about the id, the url, the state, and the name of the game.
        An attribute is added if the game is in need of attention, e.g: its the
        users turn or the game is not yet started or the user is invited to
        this game.
        """
        root = self._call_api(self.URL_HEADQUARTER, True)
        need_attention = root.inNeedOfAttention
        
        # <game inNeedOfAttention="true">
        #   <id>181897</id>
        #   <name>Stirling's Aruba</name>
        #   <state>running</state>
        #   <since>54 minutes</since>
        #   <rated>false</rated>
        #   <link>http://weewar.com/game/181897</link>
        #   <url>http://weewar.com/game/181897</url>
        #   <map>38297</map>
        #   <factionState>playing</factionState>
        # </game>
        def _parse(node):
            game = dict((child.tag, child.pyval) 
                for child in node.iterchildren())
            game['inNeedOfAttention'] = node.get('inNeedOfAttention')=='true'
            return game
        games = map(_parse, root.findall('game'))
        return need_attention, games

    def _parse_game(self, node):
        """
        Returns a simple dict for a game node.
        Example XML::

            <game id="181897">
                <id>181897</id>
                <name>Stirling's Aruba</name>
                <round>1</round>
                <state>running</state>
                <pendingInvites>true</pendingInvites>
                <pace>86400</pace>
                <type>Basic</type>
                <url>http://weewar.com/game/181897</url>
                <rated>false</rated>
                <since>1 hour 52 minutes</since>
                <players>
                    <player index="0">basti688</player>
                </players>
                <disabledUnitTypes>
                    <type>Hovercraft</type>
                    <type>Battleship</type>
                </disabledUnitTypes>
                <map>38297</map>
                <mapUrl>http://weewar.com/map/38297</mapUrl>
                <creditsPerBase>100</creditsPerBase>
                <initialCredits>300</initialCredits>
                <playingSince>Wed Jul 29 11:00:56 UTC 2009</playingSince>
            </game>

        """
        # these nodes have attributes
        # or childnodes
        complex_types = [
            'players', 
            'disabledUnitTypes'
        ]
        values = dict(
            (child.tag, child.pyval) 
            for child in node.iterchildren()
            if child.tag not in complex_types
        )
        #values['id'] = node.get('id')
        def _attrs(node, required, optional=None):
            attrs = {}
            for attr, type_ in required.items():
                try:
                    if type_ == bool:
                        attrs[attr] = node.get(attr).lower()=='true'
                    else:
                        attrs[attr] = type_(node.get(attr))
                except AttributeError:
                    attrs[attr] = node.get(attr)
            if optional:
                for attr, type_ in optional.items():
                    try:
                        if type_ == bool:
                            attrs[attr] = node.get(attr).lower()=='true'
                        else:
                            attrs[attr] = type_(node.get(attr))
                    except AttributeError:
                        pass
            return attrs
        values['players'] = [
            dict(username=player, 
                 **_attrs(player, {'index' : int, 'result' : str}, 
                          {'current' : bool}))
            for player in node.players.iterchildren()
        ]
        values['disabledUnitTypes'] = node.disabledUnitTypes.findall('type')
        return values

    def _parse_map(self, node):
        """
        Returns a simple dict for a map node.
        Example XML::

            <maps>
                <map id="42552">
                    <name>Trench Warfare - Balanced</name>
                    <initialCredits>200</initialCredits>
                    <perBaseCredits>100</perBaseCredits>
                    <width>30</width>
                    <height>10</height>
                    <maxPlayers>2</maxPlayers>
                    <url>http://weewar.com/map/42552</url>
                    <thumbnail>http://weewar.com/images/maps/boardThumb_42552_ir2.png</thumbnail>
                    <preview>http://weewar.com/images/maps/preview_42552_ir2.png</preview>
                    <revision>2</revision>
                    <creator>General_Death</creator>
                    <creatorProfile>http://weewar.com/user/General_Death</creatorProfile>
                </map>
                ...
            </maps>

        """
        values = dict((child.tag, child.pyval) 
                      for child in node.iterchildren())
        values['id'] = int(node.get('id'))
        return values

    def _parse_user(self, node):
        """
        Returns a simple dict for a user node.
        Example XML::

            <?xml version="1.0" encoding="UTF-8"?>
            <user name="basti688" id="12918">
                <points>1500</points>
                <profile>http://weewar.com/user/basti688</profile>
                <draws>0</draws>
                <victories>0</victories>
                <losses>0</losses>
                <accountType>Basic</accountType>
                <on>false</on>
                <readyToPlay>false</readyToPlay>
                <gamesRunning>1</gamesRunning>
                <lastLogin>2009-07-29 10:55:46.0</lastLogin>
                <basesCaptured>0</basesCaptured>
                <creditsSpent>200</creditsSpent>
                <favoriteUnits>
                    <unit code="lighttank" />
                </favoriteUnits>
                <preferredPlayers>
                    <player name="EgoBruiser" id="35086" />
                    <player name="bobbob" id="25808" />
                    <player name="MerissaofBulb" id="39154" />
                </preferredPlayers>
                <games>
                    <game name="game?">173101</game>
                    <game name="This is going to be long">169581</game>
                </games>
                <maps>
                    <map>36991</map>
                    <map>42196</map>
                    <map>42317</map>
                </maps>
            </user>
        """
        # these nodes have attributes
        # or childnodes
        complex_types = [
            'favoriteUnits', 
            'games', 
            'maps', 
            'preferredPlayers', 
        ]
        values = dict(
            (child.tag, child.pyval) 
            for child in node.iterchildren()
            if child.tag not in complex_types
        )
        values['name'] = node.get('name')
        values['id'] = int(node.get('id'))
        values['games'] = [
            dict(id=child.pyval, name=child.get('name')) 
            for child in node.games.iterchildren()
            if child.tag == 'game'
        ]
        values['favoriteUnits'] = [
            child.get('code') 
            for child in node.favoriteUnits.iterchildren()
            if child.tag == 'unit'
        ]
        values['preferredPlayers'] = [
            self._parse_attrs(child, id=int, name=str)
            for child in node.preferredPlayers.iterchildren()
            if child.tag == 'player'
        ]
        values['maps'] = [child.pyval
            for child in node.maps.iterchildren()
            if child.tag == 'map'
        ]
        return values 

class ServerError (Exception):
    """
    Something went completely berserk on the server!
    """

class AuthenticationError (Exception):
    """
    The submitted user credentials were not correct.
    """

#{ Basic unit types 
TROOPER = 'Trooper'
RAISER = 'Raider'
HEAVY_TROOPER = 'Heavy Trooper'
TANK = 'Tank'
HEAVY_TANK = 'Heavy Tank'
LIGHT_ARTILLERY = 'Light Artillery'
HEAVY_ARTILLERY = 'Heavy Artillery'
#} Basic unit types 

#{ PRO-account unit types 
ANTI_AIRCRAFT = 'Anti Aircraft' 
ASSAULT_ARTILLERY = 'Assault Artillery' 
BATTLESHIP = 'Battleship' 
BOMBER = 'Bomber' 
DESTROYER = 'Destroyer' 
JET = 'Jet' 
HELICOPTER = 'Helicopter' 
HOVERCRAFT = 'Hovercraft' 
SPEEDBOAT = 'Speedboat' 
SUBMARINE = 'Submarine' 
DFA = 'DFA' 
BERSERKER = 'Berserker'
#} PRO-account unit types 

class ELIZA (ReadOnlyAPI):

    """
    Weewar Bot-API (ELIZA)
    ======================

    In order for ELIZA to accept request the username MUST start with "ai_"
    This is so bots are recognizable by the community as such.

    According to the website (last updated 2009-04-06)
    > You can not register a user name with a "_" in it at the moment, however
    > you can change the name in your settings after the initial registration
    > to comply with the Eliza requirements. The registration process will soon
    > be fixed accordingly.
    
    Documentation is available at http://weewar.wikispaces.com/api.
    """

    URL_GAME_STATE = 'http://weewar.com/api1/gamestate/%s'

    def game_state(self, id):
        """
        Offers more information about the state of a game - an extended
        version of L{game()}.
        """
        try:
            root = self._call_api(self.URL_GAME_STATE % id, True)
            return self._parse_game_state(root)
        except HTTPError, e:
            if e.code==404:
                raise GameNotFound(id)
            elif e.code==403:
                raise NotYourGame(id)
            else:
                raise

    def _parse_game_state(self, node):
        """
        Returns a simple dict for a game state node.
        Example XML::

            <game>
                <id>130915</id>
                <name>test5</name>
                <round>1</round>
                <state>running</state>
                <pendingInvites>false</pendingInvites>
                <pace>86400</pace>
                <type>Pro</type>
                <url>http://weewar.com/game/130915</url>
                <rated>false</rated>
                <players>
                    <player current='true' >xx</player>
                    <player  >ai_xx</player>
                </players>
                <disabledUnitTypes>
                    <type>Speedboat</type>
                    <type>Battleship</type>
                </disabledUnitTypes>
                <map>34671</map>
                <mapUrl>http://weewar.com/map/34671</mapUrl>
                <creditsPerBase>100</creditsPerBase>
                <initialCredits>200</initialCredits>
                <playingSince>Sun Jan 04 07:40:47 UTC 2009</playingSince>
                <factions>
                    <faction current='true' playerId='36133' playerName='Gorbusch'  state='playing'  >
                    <unit x='4' y='2' type='Trooper' quantity='10' finished='false'  />
                    <unit x='2' y='4' type='Trooper' quantity='10' finished='false'  />
                    <terrain x='0' y='0' type='Harbor' finished='false' />
                    <terrain x='3' y='2' type='Base' finished='false' />
                    <terrain x='2' y='2' type='Airfield' finished='false' />
                    <terrain x='2' y='3' type='Base' finished='false' />
                    </faction>
                    <faction  playerId='52971' playerName='ai_Gorbusch' credits='200' state='playing'  > <!-- credit only available for your own faction -->
                    <unit x='5' y='7' type='Trooper' quantity='10' finished='false'  /> <!--finished will only be set to true after all movements and attacks-->
                    <unit x='7' y='5' type='Trooper' quantity='10' finished='false'  />
                    <terrain x='6' y='7' type='Base' finished='false' /> <!-- finished seems not to be set at the moment for terrain -->
                    <terrain x='9' y='9' type='Harbor' finished='false' />
                    <terrain x='7' y='6' type='Base' finished='false' />
                    <terrain x='7' y='7' type='Airfield' finished='false' />
                    </faction>
                </factions>
            </game>
        
        """
        complex_types = [
            'players', 
            'disabledUnitTypes',
            'factions',
        ]
        #values = {}
        #for child in node.iterchildren():
        #    if child.tag not in complex_types:
        #        print child.tag
        #        values[child.tag] = child.pyval
        values = dict(
            (child.tag, child.pyval) 
            for child in node.iterchildren()
            if child.tag not in complex_types
        )
        values['disabledUnitTypes'] = [
            child.pyval
            for child in node.disabledUnitTypes.iterchildren()
            if child.tag == 'type'
        ]

        def _parse_player(node):
            values = self._parse_attrs(node, index=int, current=bool, result=str)
            values['username'] = node.pyval
            return values

        values['players'] = map(_parse_player, node.players.iterchildren())

        _parse_unit = lambda node: self._parse_attrs(node, x=int, y=int, 
                                    type=str, quantity=int, finished=bool)
        _parse_terrain = lambda node: self._parse_attrs(node, x=int, y=int, 
                                    type=str, finished=bool)

        def _parse_faction(node):
            values = self._parse_attrs(node, playerId=int, playerName=str, 
                                        credits=int, state=str, current=bool, 
                                        result=str)
            values['units'] = map(_parse_unit, node.findall('unit'))
            values['terrain'] = map(_parse_terrain, node.findall('terrain'))
            return values

        values['factions'] = map(_parse_faction, node.factions.iterchildren())

        return values 

    URL_MAP_LAYOUT = 'http://weewar.com/api1/map/%s'

    def map_layout(self, id):
        """
        Complete map layout.
        """
        try:
            root = self._call_api(self.URL_MAP_LAYOUT % id)
            return self._parse_map_layout(root)
        except HTTPError, e:
            if e.code==404:
                raise MapNotFound(id)
            else:
                raise

    def _parse_map_layout(self, node):
        """
        Returns a simple dict for a game state node.
        Example XML::

            <?xml version="1.0" encoding="UTF-8"?>
            <map id="8">
                <name>One on one</name>
                <initialCredits>300</initialCredits>
                <perBaseCredits>100</perBaseCredits>
                <width>22</width>
                <height>15</height>
                <maxPlayers>2</maxPlayers>
                <url>http://weewar.com/map/8</url>
                <thumbnail>http://weewar.com/images/maps/boardThumb_8_ir3.png</thumbnail>
                <preview>http://weewar.com/images/maps/preview_8_ir3.png</preview>
                <revision>2</revision>
                <creator>alex</creator>
                <creatorProfile>http://weewar.com/user/alex</creatorProfile>
                <terrains>
                    <terrain x="0" y="7" type="Plains" />
                    ...
                    <terrain startUnit="Trooper" startUnitOwner="1" startFaction="1" x="3" y="8" type="Base" />
                    <terrain startUnit="Trooper" startUnitOwner="1" startFaction="1" x="10" y="13" type="Base" />
                    <terrain startUnit="Trooper" startUnitOwner="0" startFaction="0" x="12" y="2" type="Base" />
                    <terrain startUnit="Trooper" startUnitOwner="0" startFaction="0" x="19" y="3" type="Base" />
                    ...
                </terrains>
            </map>
        """
        complex_types = ['terrains']
        values = dict(
            (child.tag, child.pyval) 
            for child in node.iterchildren()
            if child.tag not in complex_types
        )
        values['id'] = int(node.get('id'))
        _parse_terrain = lambda node: self._parse_attrs(node, x=int, y=int, 
                type=str, startUnit=str, startUnitOwner=str, startFaction=int)
        values['terrains'] = map(_parse_terrain, node.terrains.iterchildren())
        return values

    URL_ELIZA_COMMANDS = 'http://weewar.com/api1/eliza'
    ELEMENT = objectify.ElementMaker(annotate=False, nsmap={})

    def _game_command(self, game_id, node):
        game = self.ELEMENT.weewar(game=str(game_id))
        game.append(node)
        #print tostring(game, pretty_print=True)
        node = self._call_api(self.URL_ELIZA_COMMANDS, True, tostring(game))
        if node.tag == 'error':
            if node.text == 'Game not found':
                raise GameNotFound(game_id)
            elif node.text == 'Not your turn.':
                raise NotYourTurn
            else:
                raise ELIZAError(node)
        # otherwise return parsed XML node
        return node

    #{ simple game commands
    FINISH_TURN = 'finishTurn'
    ACCEPT_INVITATION = 'acceptInvitation'
    DECLINE_INVITATION = 'declineInvitation'
    SEND_REMINDER = 'sendReminder'
    SURRENDER = 'surrender'
    ABANDON = 'abandon'
    REMOVE_GAME = 'removeGame'

    def _simple_game_command(self, game_id, cmd):
        """
        Send a simple command to the API. A simple command usually consists of 
        only one element.
        """
        node = getattr(self.ELEMENT, cmd)()
        return self._game_command(game_id, node)
    #} simple game commands

    def chat(self, game_id, msg):
        """
        Sends a (preferably polite) message.
        """
        node = self._game_command(game_id, self.ELEMENT.chat(msg))
        return True

    def build(self, game_id, (x, y), type):
        """
        Builds a unit are a specific location of the map.
        """
        try:
            node = self._game_command(game_id, self.ELEMENT.build(
                    x=str(x), y=str(y), type=str(type)))
            return node.tag == 'ok'
        except ELIZAError, e:
            if e.node.text == 'Not enough credits.':
                raise NotEnoughCredits(type)
            if e.node.text == 'Not your terrain.':
                raise NotYourTerrain(x, y)
            elif e.node.text == ('Cannot build any more units in this turn on '
                               'this coordinate.'):
                raise CannotBuildMoreUnitsHere(x, y)
            elif e.node.text == 'This Terrain cannot build the requested unit.':
                raise WrongTerrain(x, y)
            elif e.node.text == 'Blocked by a unit.':
                raise FieldIsBlocked(x, y)
            # otherwise
            return False
        
    def move_options(self, game_id, (x, y), type):
        """
        Requests unit movement options. This is pretty much like what you get 
        when you select a unit in a regular game.
        """
        try:
            options = self.ELEMENT.movementOptions(x=str(x), y=str(y), 
                                                 type=str(type))
            node = self._game_command(game_id, options)
            coords = map(lambda node: self._parse_attrs(node, x=int, y=int), 
                         node.findall('coordinate'))
            return [(c.get('x'), c.get('y')) for c in coords]
        except ELIZAError, e:
            return []
        
    def attack_options(self, game_id, (x, y), type, moved=None):
        """
        Requests possible targets. The 'moved' attribute is optional and 
        describes the number of turns a unit has already moved. This is helpful 
        for Jets and Battleships.
        """
        try:
            options = self.ELEMENT.attackOptions(x=str(x), y=str(y), 
                                                 type=str(type))
            if moved is not None:
                options.set('moved', str(moved))
            node = self._game_command(game_id, options)
            return node.tag == 'ok'
        except ELIZAError, e:
            return False
        
    def _unit_command(self, game_id, (x, y), command, **kwargs):
        """
        Send a command to a unit at (x, y).
        """
        try:
            unit = self.ELEMENT.unit(x=str(x), y=str(y))
            unit.append(getattr(self.ELEMENT, command)(**kwargs))
            return self._game_command(game_id, unit)
        except ELIZAError, e:
            if e.node.text == 'Not your Unit.':
                raise NotYourUnit(x, y)
            # otherwise simply re-raise
            raise
    

class UserNotFound (Exception):
    """
    The specified weewar game could not be found.
    """

class GameNotFound (Exception):
    """
    The specified weewar game could not be found.
    """

class MapNotFound (Exception):
    """
    The specified weewar map could not be found.
    """

class ELIZAError (Exception):
    """
    Generic ELIZA exception which is raised when a <error> element is returned.
    """
    def __init__(self, node):
        self.node = node
    def __str__(self):
        return tostring(self.node)

class NotYourGame (Exception):
    """
    Mind your own business!
    """

class NotYourTurn (Exception):
    """
    The user has to wait his/her turn to submit commands for a game.
    """

class NotYourTerrain (Exception):
    """
    The user has to capture that base first.
    """
    
class NotYourUnit (Exception):
    """
    The user has to keep his/her hands off foreign units.
    """
    
class CannotBuildMoreUnitsHere (Exception):
    """
    Cannot build any more units in this turn on this coordinate.
    """
    
class NotEnoughCredits (Exception):
    """
    Not enough credits.
    """
    
class WrongTerrain (Exception):
    """
    This Terrain cannot build the requested unit.
    """
    
class FieldIsBlocked (Exception):
    """
    Blocked by a unit.
    """

#{ shortcuts/wrapper functions

def game(id):
    """
    Returns the status of a game and gives information about the participating
    players.
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: dict
    """
    api = ReadOnlyAPI()
    return api.game(id)
    
def open_games():
    """
    Returns all currently available open games as a list of IDs.
    @rtype: [int]
    """
    api = ReadOnlyAPI()
    return api.open_games()
    
def all_users():
    """
    Returns a list of all users who have been online in the last 7 days,
    including their current ranking.
    @rtype: dict
    """
    api = ReadOnlyAPI()
    return api.all_users()
    
def user(username):
    """
    Returns detailed information about a single user, including everything that
    is visible on the profile page and the games the user is participating in.
    @param unsername: Unique unsername of weewar player.
    @type id: str
    @rtype: dict
    """
    api = ReadOnlyAPI()
    return api.user(username)

def latest_maps():
    """
    Returns the latest published maps including urls for previews, images, and
    other details.
    @rtype: dict
    """
    api = ReadOnlyAPI()
    return api.latest_maps()
    
def headquarter(username, apikey):
    """
    Returns all games that are listed in your Headquarters. Includes
    information about the id, the url, the state, and the name of the game.  An
    attribute is added if the game is in need of attention, e.g: its the users
    turn or the game is not yet started or the user is invited to this game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @return: A tuple containing (<games in need of attention>, [<game info>])
    @rtype: (int, [dict, ...])
    """
    api = ReadOnlyAPI(username, apikey)
    return api.headquarter()

def game_state(username, apikey, id):
    """
    Offers more information about the state of a game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: dict
    """
    api = ELIZA(username, apikey)
    return api.game_state(id)

def map_layout(id):
    """
    Returns complete map layout.
    @param id: Unique ID of weewar map.
    @type id: int
    @rtype: dict
    """
    api = ELIZA()
    return api.map_layout(id)
    

def finish_turn(username, apikey, id):
    """
    Finishes turn in game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: bool
    """
    try:
        api = ELIZA(username, apikey)
        node = api._simple_game_command(id, api.FINISH_TURN)
        return node.tag == 'ok'
    except NotYourTurn:
        return False

def accept_invitation(username, apikey, id):
    """
    Accepts invitation to game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: bool
    """
    try:
        api = ELIZA(username, apikey)
        node = api._simple_game_command(id, api.ACCEPT_INVITATION)
        return node.tag == 'ok'
    except ELIZAError, e:
        if e.node.text == 'You have already accepted the invitation.':
            return False
        else:
            raise

def decline_invitation(username, apikey, id):
    """
    Declines invitation to game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: bool
    """
    try:
        api = ELIZA(username, apikey)
        node = api._simple_game_command(id, api.DECLINE_INVITATION)
        return node.tag == 'ok'
    except ELIZAError, e:
        if e.node.text == 'Cannot decline an invitation.':
            return False
        else:
            raise

def send_reminder(username, apikey, id):
    """
    Sends a reminder about the game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: bool
    """
    try:
        api = ELIZA(username, apikey)
        node = api._simple_game_command(id, api.SEND_REMINDER)
        return node.tag == 'ok'
    except ELIZAError, e:
        if e.node.text == 'Can not remind current player.':
            return False
        else:
            raise

def surrender_game(username, apikey, id):
    """
    Surrender!
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: bool
    """
    try:
        api = ELIZA(username, apikey)
        node = api._simple_game_command(id, api.SURRENDER)
        return node.tag == 'ok'
    except ELIZAError, e:
        if e.node.text in ['Can not surrender.',
                           'Game is not running.']:
            return False
        else:
            raise

def abandon_game(username, apikey, id):
    """
    Abondons game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: bool
    """
    try:
        api = ELIZA(username, apikey)
        node = api._simple_game_command(id, api.ABANDON)
        return node.tag == 'ok'
    except ELIZAError, e:
        if e.node.text == 'Game is not running.':
            return False
        else:
            raise

def remove_game(username, apikey, id):
    """
    Removes game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param id: Unique ID of weewar game.
    @type id: int
    @rtype: bool
    """
    try:
        api = ELIZA(username, apikey)
        node = api._simple_game_command(id, api.REMOVE_GAME)
        return node.tag == 'ok'
    except ELIZAError, e:
        if e.node.text == 'Game has already been deleted.':
            return False
        else:
            raise

def chat(username, apikey, game_id, msg):
    """
    Sends a chat message to the game board.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param game_id: Unique ID of weewar game.
    @type game_id: int
    @param msg: Message
    @type msg: str
    """
    api = ELIZA(username, apikey)
    return api.chat(game_id, msg)

def build_unit(username, apikey, game_id, (x, y), unit):
    """
    Sends a chat message to the game board.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param game_id: Unique ID of weewar game.
    @type game_id: int
    @param x: X-position on map.
    @type x: int
    @param y: Y-position on map.
    @type y: int
    @param unit: Unit type to build.
    @type unit: str
    """
    api = ELIZA(username, apikey)
    return api.build(game_id, (x, y), unit)

def unit_move_options(username, apikey, game_id, unit, (x, y)):
    """
    Requests unit movement options. This is pretty much like what you get 
    when you select a unit in a regular game.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param game_id: Unique ID of weewar game.
    @type game_id: int
    @param unit: Unit type.
    @type unit: str
    @param x: X-position on map.
    @type x: int
    @param y: Y-position on map.
    @type y: int
    """
    api = ELIZA(username, apikey)
    return api.move_options(game_id, (x, y), unit)

def unit_attack_options(username, apikey, game_id, unit, (x, y), moved=None):
    """
    Requests possible targets. The 'moved' attribute is optional and 
    describes the number of turns a unit has already moved. This is helpful 
    for Jets and Battleships.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param game_id: Unique ID of weewar game.
    @type game_id: int
    @param unit: Unit type.
    @type unit: str
    @param x: X-position on map.
    @type x: int
    @param y: Y-position on map.
    @type y: int
    """
    api = ELIZA(username, apikey)
    return api.attack_options(game_id, (x, y), unit, moved)

def move_unit(username, apikey, game_id, unit, from_, to):
    """
    Move a unit from C{from_} to C{to}.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param game_id: Unique ID of weewar game.
    @type game_id: int
    @param unit: Unit type.
    @type unit: str
    @param from_: position on map.
    @type from_: (int, int)
    @param to: position on map.
    @type to: (int, int)
    """
    api = ELIZA(username, apikey)
    to = dict(zip('xy', map(str, to)))
    return api._unit_command(game_id, from_, 'move', **to)
    
def attack_with(username, apikey, game_id, unit, from_, target):
    """
    Attack with unit at C{from_} to C{to}.
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param game_id: Unique ID of weewar game.
    @type game_id: int
    @param unit: Unit type.
    @type unit: str
    @param from_: position on map.
    @type from_: (int, int)
    @param target: position on map.
    @type target: (int, int)
    """
    api = ELIZA(username, apikey)
    to = dict(zip('xy', map(str, target)))
    return api._unit_command(game_id, from_, 'attack', **to)
    
def capture_base(username, apikey, game_id, unit, at):
    """
    Capture a base with unit. You have to move there first! 
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param game_id: Unique ID of weewar game.
    @type game_id: int
    @param unit: Unit type.
    @type unit: str
    @param at: position on map.
    @type at: (int, int)
    """
    api = ELIZA(username, apikey)
    return api._unit_command(game_id, from_, 'capture')

def repair_unit(username, apikey, game_id, unit, at):
    """
    Repair a unit. 
    @param username: weewar username
    @type username: str
    @param apikey: Matching API key (from http://weewar.com/apiToken)
    @type apikey: str
    @param game_id: Unique ID of weewar game.
    @type game_id: int
    @param unit: Unit type.
    @type unit: str
    @param at: position on map.
    @type at: (int, int)
    """
    api = ELIZA(username, apikey)
    return api._unit_command(game_id, from_, 'repair')

#} shortcuts/wrapper functions

#if __name__ == '__main__':
#    
#    # Put your Weewar username and API key in file ~/.weewar-apikey separated by
#    # a colon (:) with one user-key-pair per line:
#    # 
#    #    someuser:XXXXXXXX
#    #    someotheruser:XXXXXXXXXXXXXXX
#    #    ...
#    # 
#    # If you have more than one entry (which is nice for testing) only the first 
#    # is used.
#    import os.path
#    keys = open(os.path.expanduser('~/.weewar-apikey')).readlines()
#    user, key = keys.pop(0).strip().split(':')
#
#    print open_games()
#    print all_users()
#    u = user(user)
#    print 'User %(name)s (%(points)s points)' % u,
#    print 'has %i games:' % len(u['games'])
#    for g in u['games']:
#        print ' - %(name)s (%(url)s)' % game(g['id'])
#    print latest_maps()
#    print headquarter(user, key)
#
#    game_id = 186136
#    print game_state(user, key, game_id)
#    print map_layout(8)
#    print finish_turn(user, key, game_id)
#    print accept_invitation(user, key, game_id)
#    print decline_invitation(user, key, game_id)
#    print send_reminder(user, key, game_id)
#    print surrender_game(user, key, game_id)
#    print abandon_game(user, key, game_id)
#    print remove_game(user, key, game_id)
#    print chat(user, key, game_id, 'bla'*10)
#    print build(user, key, game_id, (4, 14), TANK)
#    print unit_move_options(user, key, game_id, TROOPER, (2, 11))
#    print unit_attack_options(user, key, game_id, TROOPER, (2, 11))
#    print move_unit(user, key, game_id, TROOPER, (2, 11), (3, 12))
#    print attack_with(user, key, game_id, TROOPER, (4, 13), (4, 11))

