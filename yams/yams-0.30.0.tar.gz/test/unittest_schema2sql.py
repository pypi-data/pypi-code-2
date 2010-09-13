# copyright 2004-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of yams.
#
# yams is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# yams is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with yams. If not, see <http://www.gnu.org/licenses/>.
"""unit tests for module yams.schema2sql
"""

import os.path as osp
from cStringIO import StringIO

from logilab.common.testlib import TestCase, unittest_main
from logilab.database import get_db_helper

from yams.reader import SchemaLoader
from yams import schema2sql

schema2sql.SET_DEFAULT = True

DATADIR = osp.abspath(osp.join(osp.dirname(__file__), 'data'))

schema = SchemaLoader().load([DATADIR])


EXPECTED_DATA_NO_DROP = """
CREATE TABLE Affaire(
 sujet varchar(128),
 ref varchar(12),
 inline_rel integer
);
CREATE INDEX affaire_inline_rel_idx ON Affaire(inline_rel);

CREATE TABLE Company(
 name text
);

CREATE TABLE Datetest(
 dt1 timestamp,
 dt2 timestamp,
 d1 date,
 d2 date,
 t1 time,
 t2 time
);

CREATE TABLE Division(
 name text
);

CREATE TABLE EPermission(
 name varchar(100) NOT NULL
);
CREATE INDEX epermission_name_idx ON EPermission(name);

CREATE TABLE Eetype(
 name varchar(64) UNIQUE NOT NULL,
 description text,
 meta boolean,
 final boolean,
 initial_state integer
);
CREATE INDEX eetype_name_idx ON Eetype(name);
CREATE INDEX eetype_initial_state_idx ON Eetype(initial_state);

CREATE TABLE Employee(
);

CREATE TABLE Note(
 date varchar(10),
 type varchar(1),
 para varchar(512)
);

CREATE TABLE Person(
 nom varchar(64) NOT NULL,
 prenom varchar(64),
 sexe varchar(1) DEFAULT 'M',
 promo varchar(6),
 titre varchar(128),
 adel varchar(128),
 ass varchar(128),
 web varchar(128),
 tel integer,
 fax integer,
 datenaiss date,
 test boolean,
 salary float
);
CREATE UNIQUE INDEX unique_person_nom_prenom_idx ON Person(nom,prenom);

CREATE TABLE Societe(
 nom varchar(64),
 web varchar(128),
 tel integer,
 fax integer,
 rncs varchar(32),
 ad1 varchar(128),
 ad2 varchar(128),
 ad3 varchar(128),
 cp varchar(12),
 ville varchar(32)
);

CREATE TABLE State(
 eid integer PRIMARY KEY,
 name varchar(256) NOT NULL,
 description text
);
CREATE INDEX state_name_idx ON State(name);

CREATE TABLE Subcompany(
 name text
);

CREATE TABLE Subdivision(
 name text
);

CREATE TABLE pkginfo(
 modname varchar(30) NOT NULL,
 version varchar(10) DEFAULT '0.1' NOT NULL,
 copyright text NOT NULL,
 license varchar(3),
 short_desc varchar(80) NOT NULL,
 long_desc text NOT NULL,
 author varchar(100) NOT NULL,
 author_email varchar(100) NOT NULL,
 mailinglist varchar(100),
 debian_handler varchar(6)
);


CREATE TABLE concerne_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT concerne_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX concerne_relation_from_idx ON concerne_relation(eid_from);
CREATE INDEX concerne_relation_to_idx ON concerne_relation(eid_to);

CREATE TABLE division_of_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT division_of_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX division_of_relation_from_idx ON division_of_relation(eid_from);
CREATE INDEX division_of_relation_to_idx ON division_of_relation(eid_to);

CREATE TABLE evaluee_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT evaluee_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX evaluee_relation_from_idx ON evaluee_relation(eid_from);
CREATE INDEX evaluee_relation_to_idx ON evaluee_relation(eid_to);

CREATE TABLE next_state_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT next_state_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX next_state_relation_from_idx ON next_state_relation(eid_from);
CREATE INDEX next_state_relation_to_idx ON next_state_relation(eid_to);

CREATE TABLE obj_wildcard_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT obj_wildcard_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX obj_wildcard_relation_from_idx ON obj_wildcard_relation(eid_from);
CREATE INDEX obj_wildcard_relation_to_idx ON obj_wildcard_relation(eid_to);

CREATE TABLE require_permission_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT require_permission_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX require_permission_relation_from_idx ON require_permission_relation(eid_from);
CREATE INDEX require_permission_relation_to_idx ON require_permission_relation(eid_to);

CREATE TABLE state_of_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT state_of_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX state_of_relation_from_idx ON state_of_relation(eid_from);
CREATE INDEX state_of_relation_to_idx ON state_of_relation(eid_to);

CREATE TABLE subcompany_of_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT subcompany_of_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX subcompany_of_relation_from_idx ON subcompany_of_relation(eid_from);
CREATE INDEX subcompany_of_relation_to_idx ON subcompany_of_relation(eid_to);

CREATE TABLE subdivision_of_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT subdivision_of_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX subdivision_of_relation_from_idx ON subdivision_of_relation(eid_from);
CREATE INDEX subdivision_of_relation_to_idx ON subdivision_of_relation(eid_to);

CREATE TABLE subj_wildcard_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT subj_wildcard_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX subj_wildcard_relation_from_idx ON subj_wildcard_relation(eid_from);
CREATE INDEX subj_wildcard_relation_to_idx ON subj_wildcard_relation(eid_to);

CREATE TABLE sym_rel_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT sym_rel_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX sym_rel_relation_from_idx ON sym_rel_relation(eid_from);
CREATE INDEX sym_rel_relation_to_idx ON sym_rel_relation(eid_to);

CREATE TABLE travaille_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT travaille_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX travaille_relation_from_idx ON travaille_relation(eid_from);
CREATE INDEX travaille_relation_to_idx ON travaille_relation(eid_to);

CREATE TABLE works_for_relation (
  eid_from INTEGER NOT NULL,
  eid_to INTEGER NOT NULL,
  CONSTRAINT works_for_relation_p_key PRIMARY KEY(eid_from, eid_to)
);

CREATE INDEX works_for_relation_from_idx ON works_for_relation(eid_from);
CREATE INDEX works_for_relation_to_idx ON works_for_relation(eid_to);
"""

class SQLSchemaTC(TestCase):

    def test_known_values(self):
        dbhelper = get_db_helper('postgres')
        output = schema2sql.schema2sql(dbhelper, schema)
        self.assertTextEquals(EXPECTED_DATA_NO_DROP.strip(), output.strip())


if __name__ == '__main__':
    unittest_main()
