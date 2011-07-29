css=""".gray-0 {
  background-color: hsl(0, 0%, 100%);
}
.gray-1 {
  background-color: hsl(0, 0%, 98%);
}
.gray-2 {
  background-color: hsl(0, 0%, 96%);
}
.gray-3 {
  background-color: hsl(0, 0%, 94%);
}
.gray-4 {
  background-color: hsl(0, 0%, 92%);
}
.gray-5 {
  background-color: hsl(0, 0%, 90%);
}
.gray-6 {
  background-color: hsl(0, 0%, 88%);
}
.gray-7 {
  background-color: hsl(0, 0%, 86%);
}
.gray-8 {
  background-color: hsl(0, 0%, 84%);
}
table.natto_container {
  background: #eee;
  display: table;
  border-radius: 3px;
  border-spacing: 1px;
  box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.5);
  margin-bottom: 10px;
  font-size: 9pt;
}
table.natto_container th {
  padding: 3px;
  background: #ffa500;
  color: #583900;
  text-align: left;
  font-size: small;
  font-weight: normal;
  border-radius: 2px;
  font-family: Consolas, Lucida Console, Monaco, monospace;
}
table.natto_container th span.label {
  font-weight: bold;
  color: #5a00a3;
}
table.natto_container td {
  padding: 0px;
}
table.natto_container span.border_spaces,
table.natto_container span.tabs {
  background-image: -webkit-linear-gradient(left, #eeeeee 0%, #eeeeee 1px, #f5f5f5 1px,
    #f5f5f5 100%);
  background-image: -moz-linear-gradient(left, #eeeeee 0%, #eeeeee 1px, #f5f5f5 1px,
    #f5f5f5 100%);
  background-image: -ms-linear-gradient(left, #eeeeee 0%, #eeeeee 1px, #f5f5f5 1px,
    #f5f5f5 100%);
  background-image: -o-linear-gradient(left, #eeeeee 0%, #eeeeee 1px, #f5f5f5 1px,
    #f5f5f5 100%);
  background-image: linear-gradient(left center, #eeeeee 0px, #eeeeee 1px, #f5f5f5 1px,
    #f5f5f5 1px);
}
table.natto_container div.skipped {
  color: #888;
}
table.natto_container span.html_tag {
  color: blue;
}
table.natto_container div.recursion {
  white-space: nowrap;
  color: red;
}
table.natto_container div.max_depth {
  white-space: nowrap;
  color: red;
}
table.natto_container div.max_i {
  white-space: nowrap;
  color: red;
}
table.natto_container div.docstring_container {
  background: #ffff8e;
  padding: 1px;
  border-radius: 3px;
  border: 2px solid #f1d02b;
  display: table;
}
table.natto_container div.docstring_expander {
  padding-left: 20px;
  width: 14px;
  height: 14px;
  display: table;
  background: url(data:image/gif;base64,R0lGODlhDgAOAKUfADg4OEZGRldXV2dnZ3V1dX9/f5ycnJ+fn6Ojo6ysrLGxsba2tru7u8DAwMXFxcfHx8rKytPT09fX193d3d7e3uDg4OXl5ejo6Onp6evr6+7u7vHx8fT09Pf39/z8/P7+/v////7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/iwAAAAADgAOAAAGaUDQZEgsDkEYkHLJVGIkn6h0GpVEPNisFhuBdL7fQgH8hTg4aDSBkEY7Gpv4YE6PbxoMjV7A7+s1DAsZg4MBAYSDCwoXjIwAAI2MCgkWlZaXlQkIFZydnpwIDwcUpKWmBw8gBqusrasgQQA7) left top no-repeat;
}
table.natto_container div.docstring {
  padding: 4px;
  padding-top: 10px;
  white-space: pre;
  display: none;
}
table.natto_container div.value {
  font-family: Consolas, Lucida Console, Monaco, monospace;
  white-space: pre;
}
table.natto_container div.value.type_bool_true {
  font-weight: bold;
  color: #5ba800;
}
table.natto_container div.value.type_none {
  font-weight: bold;
  color: #ff9411;
}
table.natto_container div.value.type_bool_false {
  font-weight: bold;
  color: #d90014;
}
table.natto_container div.value.type_number {
  color: #3c32ff;
}
table.natto_container div.value.type_unicode {
  color: #50097c;
}
table.natto_container div.value.type_str {
  color: #000000;
}
table.natto_container div.value.type_func {
  color: #009600;
}
table.natto_container div.value.type_other {
  color: blue;
}
table.natto_container div.funcalike {
  color: green;
}
table.natto_container div.empty {
  color: #ff9411;
}
table.natto_container div.repetition {
  white-space: nowrap;
  color: #890089;
}
table.natto_container div.blacklisted {
  color: #890089;
}
table.natto_container a {
  color: #E00086;
}
table.natto_container a:hover {
  color: #960057;
}
table.natto_container a:visited {
  color: #E00086;
}
table.natto {
  border-collapse: separate;
  width: 100%;
  border-spacing: 1px;
}
table.natto th.key {
  font-family: Consolas, Lucida Console, Monaco, monospace;
  white-space: nowrap;
  border-radius: 2px;
  text-align: left;
  padding: 0px 1px 0px 1px;
  font-weight: normal;
  font-size: small;
  color: #fff;
  vertical-align: middle;
  text-shadow: 0px 1px 0px rgba(255, 255, 255, 0.3), 0px -1px 0px rgba(0, 0, 0, 0.4);
  background-color: #79ac12;
  background: hsl(80, 80%, 50%);
  background-image: -webkit-linear-gradient(-75deg, hsl(80, 80%, 35%), hsl(80, 80%, 42%));
  background-image: -moz-linear-gradient(-75deg, hsl(80, 80%, 35%), hsl(80, 80%, 42%));
  background-image: -ms-linear-gradient(-75deg, hsl(80, 80%, 35%), hsl(80, 80%, 42%));
  background-image: -o-linear-gradient(-75deg, hsl(80, 80%, 35%), hsl(80, 80%, 42%));
  background-image: linear-gradient(center, hsl(80, 80%, 35%) 0%, hsl(80, 80%, 42%) 100%);
  border: 1px solid hsl(80, 80%, 30%);
}
table.natto th.key.type_dict {
  background-color: #b71357;
  background: hsl(335, 80%, 50%);
  background-image: -webkit-linear-gradient(-75deg, hsl(335, 80%, 35%), hsl(335, 80%,
    42%));
  background-image: -moz-linear-gradient(-75deg, hsl(335, 80%, 35%), hsl(335, 80%, 42%));
  background-image: -ms-linear-gradient(-75deg, hsl(335, 80%, 35%), hsl(335, 80%, 42%));
  background-image: -o-linear-gradient(-75deg, hsl(335, 80%, 35%), hsl(335, 80%, 42%));
  background-image: linear-gradient(center, hsl(335, 80%, 35%) 0%, hsl(335, 80%,
    42%) 100%);
  border: 1px solid hsl(335, 80%, 30%);
}
table.natto th.key.type_sequence {
  background-color: #1486bf;
  background: hsl(200, 80%, 50%);
  background-image: -webkit-linear-gradient(-75deg, hsl(200, 80%, 35%), hsl(200, 80%,
    42%));
  background-image: -moz-linear-gradient(-75deg, hsl(200, 80%, 35%), hsl(200, 80%, 42%));
  background-image: -ms-linear-gradient(-75deg, hsl(200, 80%, 35%), hsl(200, 80%, 42%));
  background-image: -o-linear-gradient(-75deg, hsl(200, 80%, 35%), hsl(200, 80%, 42%));
  background-image: linear-gradient(center, hsl(200, 80%, 35%) 0%, hsl(200, 80%,
    42%) 100%);
  border: 1px solid hsl(200, 80%, 30%);
}
table.natto th.key.type_generator {
  background-color: #1486bf;
  background: hsl(100, 80%, 50%);
  background-image: -webkit-linear-gradient(-75deg, hsl(100, 80%, 35%), hsl(100, 80%,
    42%));
  background-image: -moz-linear-gradient(-75deg, hsl(100, 80%, 35%), hsl(100, 80%, 42%));
  background-image: -ms-linear-gradient(-75deg, hsl(100, 80%, 35%), hsl(100, 80%, 42%));
  background-image: -o-linear-gradient(-75deg, hsl(100, 80%, 35%), hsl(100, 80%, 42%));
  background-image: linear-gradient(center, hsl(100, 80%, 35%) 0%, hsl(100, 80%,
    42%) 100%);
  border: 1px solid hsl(100, 80%, 30%);
}
table.natto th.key.highlight {
  background-color: #ff2f11;
  background: hsl(0, 100%, 50%);
  background-image: -webkit-linear-gradient(70deg, hsl(0, 100%, 50%), hsl(0, 100%, 70%));
  background-image: -moz-linear-gradient(70deg, hsl(0, 100%, 50%), hsl(0, 100%, 70%));
  background-image: -ms-linear-gradient(70deg, hsl(0, 100%, 50%), hsl(0, 100%, 70%));
  background-image: -o-linear-gradient(70deg, hsl(0, 100%, 50%), hsl(0, 100%, 70%));
  background-image: linear-gradient(center, hsl(0, 100%, 50%) 0%, hsl(0, 100%, 70%) 100%);
  border: 1px solid hsl(0, 100%, 30%);
}
table.natto th.key.last_item {
  border-radius: 2px 2px 10px 2px;
}
table.natto tr.other_title th {
  background: #bcbcbc;
  color: #000;
  font-weight: normal;
  font-size: 9pt;
  border-radius: 2px 10px 2px 2px;
  background-color: #FFE993;
  white-space: nowrap;
  background: hsl(48, 100%, 50%);
  background-image: -webkit-linear-gradient(70deg, hsl(48, 100%, 50%), hsl(48, 100%, 55%));
  background-image: -moz-linear-gradient(70deg, hsl(48, 100%, 50%), hsl(48, 100%, 55%));
  background-image: -ms-linear-gradient(70deg, hsl(48, 100%, 50%), hsl(48, 100%, 55%));
  background-image: -o-linear-gradient(70deg, hsl(48, 100%, 50%), hsl(48, 100%, 55%));
  background-image: linear-gradient(center, hsl(48, 100%, 50%) 0%, hsl(48, 100%,
    55%) 100%);
  border: 1px solid hsl(48, 100%, 30%);
}
table.natto td {
  font-family: Consolas, Lucida Console, Monaco, monospace;
  border-radius: 2px;
  font-size: small;
  width: 100%;
  padding: 0px;
  padding-left: 1px;
}
tr.last-item th {
  background: red !important;
}

"""