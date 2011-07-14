
from turbogears import view
from turbogears.widgets.datagrid import DataGrid


def setup_module():
    if not view.engines:
        view.load_engines()


class Foo:

    def __init__(self, name, subtype, text):
        self.name = name
        self.subtype = subtype
        self.text = text

    def _get_excerpt(self):
        return self.text + '...'
    excerpt = property(_get_excerpt)

class User:

    def __init__(self, ID, name, emailAddress):
        self.userId = ID
        self.name = name
        self.emailAddress = emailAddress
    displayName = property(lambda self: self.name.capitalize())


class TestDataGrid:

    def test_column_declaration(self):
        """Test standard column declaration styles."""
        grid = DataGrid(name='grid', fields=[
            DataGrid.Column('name', options=dict(foobar=123)),
            ('Subtype', 'subtype'),
            DataGrid.Column('text', 'excerpt', 'TEXT')])
        d = dict(value='value')
        grid.update_params(d)
        get_field = d['get_field']
        # 'headers' and 'collist' only supported for backward compatibility
        assert d['headers'] == ['Name', 'Subtype', 'TEXT']
        assert d['collist'] == ['name', 'column-1', 'text']
        assert d['columns'][0].get_option('foobar') == 123
        assert grid.get_column('name').options['foobar'] == 123
        row = Foo('spa1', 'fact', 'thetext')
        assert 'spa1' == get_field(row, 'name')
        assert 'fact' == get_field(row, 'column-1')
        assert 'thetext...' == get_field(row, 'text')

    def test_alternative_column_declaration(self):
        """Test alternative column declaration styles."""
        g = lambda: None
        grid = DataGrid(fields=[
            (g), ('t', g), ('t', g, dict(p=0)),
            DataGrid.Column('n', g, 't', dict(p=0))])
        for i in range(4):
            name = i == 3 and 'n' or 'column-%d' % i
            c = grid[name]
            assert c.name == name
            title = i == 0 and name.capitalize() or 't'
            assert c.title == title
            assert c.getter == g
            options = i > 1 and dict(p=0) or dict()
            assert c.options == options

    def test_empty_column_title(self):
        """Test automatic and empty column titles."""
        grid = DataGrid(fields=[
            (None, 'a'), ('', 'a'), ('title', 'a')])
        assert grid['column-0'].title == 'Column-0'
        assert grid['column-1'].title == ''
        assert grid['column-2'].title == 'title'

    def test_column_alignment(self):
        """Test controlling column alignment."""
        grid = DataGrid(fields=[
            ('left col', lambda d: d[0]),
            ('center col', lambda d: d[1], dict(align='center')),
            ('right col', lambda d: d[2], dict(align='right'))])
        output = grid.render([('left data', 'center data', 'right data')])
        assert '<td>left data</td><td align="center">center data</td>' \
            '<td align="right">right data</td>' in output

    def test_template_overridal(self):
        """Test overriding the template."""
        grid = DataGrid(fields=[
                ('Name', 'name'),
                ('Subtype', 'subtype'),
                ('TEXT', Foo._get_excerpt)],
            template = "turbogears.fastdata.templates.datagrid")
        d = dict(value='value')
        grid.update_params(d)

    def test_wiki_samples(self):
        """Test that sample code on DataGridWidget wiki page actually works."""
        grid = DataGrid(fields=[
            ('ID', 'userId'),
            ('Name', 'displayName'),
            ('E-mail', 'emailAddress')])
        users = [User(1, 'john', 'john@foo.net'),
            User(2, 'fred', 'fred@foo.net')]
        output = grid.render(users)
        assert '<td>2</td><td>Fred</td><td>fred@foo.net</td>' in output
        grid = DataGrid(fields=[
            ('Name', lambda row: row[1]),
            ('Country', lambda row: row[2]),
            ('Age', lambda row: row[0])])
        data = [(33, "Anton Bykov", "Bulgaria"),
            (23, "Joe Doe", "Great Britain"),
            (44, "Pablo Martelli", "Brazil")]
        output = grid.render(data)
        assert '<td>Joe Doe</td><td>Great Britain</td><td>23</td>' in output
