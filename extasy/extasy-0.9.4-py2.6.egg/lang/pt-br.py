#!/usr/bin/python
# -*- coding: utf8 -*-
lang = {
    #page
    'I go to page "$url"' : 'eu navego para "$url"',
    'I see "$title" title' : 'eu vejo o título "$title"',
    'I see that current page contains "$markup"' : 'eu vejo que a página contém "$markup"',
    'I see that current page does not contain "$markup"' : 'eu vejo que a página não contém "$markup"',
    'I wait for the page to load' : 'eu espero a página carregar',
    'I wait for the page to load for $timeout seconds' : 'eu espero a página carregar por $timeout segundos',
    'I wait for $timeout seconds' : 'eu espero por $timeout segundos',
    
    #checkbox
    'I check "$label" checkbox' : 'Eu marco o checkbox "$label"',
    'I check "$label" checkbox in "$group_label" group' : 'Eu marco o checkbox "$label" do grupo "$group_label"',
    'I uncheck "$label" checkbox' : 'Eu desmarco o checkbox "$label"',
    'I uncheck "$label" checkbox in "$group_label" group' : 'Eu desmarco o checkbox "$label" do grupo "$group_label"',
    'I see that "$label" checkbox is checked' : 'Eu vejo que o checkbox "$label" está marcado',
    'I see that "$label" checkbox in "$group_label" group is checked' : 'Eu vejo que o checkbox "$label" do grupo "$group_label" está marcado',
    'I see that "$label" checkbox is not checked' : 'Eu vejo que o checkbox "$label" está desmarcado',
    'I see that "$label" checkbox in "$group_label" group is not checked' : 'Eu vejo que o checkbox "$label" do grupo "$group_label" está desmarcado',
    
    #radio
    'I check "$label" radio' : 'Eu marco o radio "$label"',
    'I check "$label" radio in "$group_label" group' : 'Eu marco o radio "$label" do grupo "$group_label"',
    'I uncheck "$label" radio' : 'Eu desmarco o radio "$label"',
    'I uncheck "$label" radio in "$group_label" group' : 'Eu desmarco o radio "$label" do grupo "$group_label"',
    'I see that "$label" radio is checked' : 'Eu vejo que o radio "$label" está marcado',
    'I see that "$label" radio in "$group_label" group is checked' : 'Eu vejo que o radio "$label" do grupo "$group_label" está marcado',
    'I see that "$label" radio is not checked' : 'Eu vejo que o radio "$label" está desmarcado',
    'I see that "$label" radio in "$group_label" group is not checked' : 'Eu vejo que o radio "$label" do grupo "$group_label" está desmarcado',
    
    #button
    'I click on "$label" button' : 'Eu clico no botão "$label"',

    #menu
    'I click on "$title" menu item' : 'Eu clico no item de menu "$title"',
    'I wait for "$title" menu item to be present' : 'Eu espero o item de menu "$title" aparecer',
    'I wait for "$title" menu item to be present for $timeout seconds' : 'Eu espero o item de menu "$title" aparecer por $timeout segundos',
    'I mouseover "$title" menu item' : 'Eu passo o mouse no item de menu "$title"',

    #tree
    'I click on "$title" tree node' : 'Eu clico no nó de árvore "$title"',
    'I wait for "$title" tree node to be present' : 'Eu espero o nó de árvore "$title" aparecer',
    'I wait for "$title" tree node to be present for $timeout seconds' : 'Eu espero o nó de árvore "$title" aparecer por $timeout segundos',
    'I open "$title" tree node' : 'Eu abro o nó de árvore "$title"',
    'I close "$title" tree node' : 'Eu fecho o nó de árvore "$title"',

    #tab
    'I click on "$title" tab' : 'Eu clico na aba "$title"',
    'I wait for "$title" tab to be present' : 'Eu espero a aba "$title" aparecer',
    'I wait for "$title" tab to be present for $timeout seconds' : 'Eu espero a aba "$title" aparecer por $timeout segundos',
    'I close "$title" tab' : 'Eu fecho a aba "$title"',
    'In "$title" tab:' : 'Na aba "$title":',
    
    #window
    'I wait for window to be present' : 'Eu espero a janela aparecer',
    'I wait for "$title" window to be present' : 'Eu espero a janela "$title" aparecer',
    'I wait for window to be present for $timeout seconds' : 'Eu espero a janela aparecer por $timeout segundos',
    'I wait for "$title" window to be present for $timeout seconds' : 'Eu espero a janela "$title" aparecer por $timeout segundos',
    'I close window' : 'Eu fecho a janela',
    'I close "$title" window' : 'Eu fecho a janela "$title"',

    #grid
    'I wait for grid to be present' : 'Eu espero o grid aparecer',
    'I wait for "$title" grid to be present' : 'Eu espero o grid "$title" aparecer',
    'I wait for grid to be present for $timeout seconds' : 'Eu espero o grid aparecer por $timeout segundos',
    'I wait for "$title" grid to be present for $timeout seconds' : 'Eu espero o grid "$title" aparecer por $timeout segundos',
    
    #grid lines
    'I wait for grid lines to be present' : 'Eu espero as linhas do grid aparecerem',
    'I wait for "$title" grid lines to be present' : 'Eu espero as linhas do grid "$title" aparecerem',
    'I wait for grid lines to be present for $timeout seconds' : 'Eu espero as linhas do grid aparecerem por $timeout segundos',
    'I wait for "$title" grid lines to be present for $timeout seconds' : 'Eu espero as linhas do grid "$title" aparecerem por $timeout segundos',
    'I click on $line line of grid' : 'Eu clico na $line linha do grid',
    'I click on $line line of "$title" grid' : 'Eu clico na $line linha do grid "$title"',
    'I doubleclick $line line of grid' : 'Eu dou um duplo clique na $line linha do grid',
    'I doubleclick $line line of "$title" grid' : 'Eu dou um duplo clique na $line linha do grid "$title"',

    #line accessors
    'first' : 'primeira',
    'last' : 'última',
    

    #textbox
    'I type "$text" in "$label" textbox' : 'Eu preencho a caixa de texto "$label" com "$text"',
    'I see that "$label" textbox is empty' : 'Eu vejo que a caixa de texto "$label" está vazia',
    'I see that "$label" textbox is not empty' : 'Eu vejo que a caixa de texto "$label" não está vazia',
    'I clean "$label" textbox' : 'Eu limpo a caixa de texto "$label"',
    
    #combo
    'I open "$label" combo' : 'Eu abro o combo "$label"',
    'I close "$label" combo' : 'Eu fecho o combo "$label"',
    'I wait for "$label" combo options to be present' : 'Eu espero as opções do combo "$label" aparecerem',
    'I wait for "$label" combo options to be present for $timeout seconds' : 'Eu espero as opções do combo "$label" aparecerem por $timeout segundos',
    'I select the option with value of "$value" in "$label" combo' : 'Eu seleciono a opção de valor "$value" no combo "$label"',
    'I select the option with index of $index in "$label" combo' : 'Eu seleciono a opção de índice $index no combo "$label"',
    'I select the option with text of "$text" in "$label" combo' : 'Eu seleciono a opção de texto "$text" no combo "$label"',
    'I see "$label" combo contains an option with text of "$text"' : 'Eu vejo que o combo "$label" contém uma opção com o texto "$text"',
    'I see "$label" combo contains an option with value of "$value"' : 'Eu vejo que o combo "$label" contém uma opção com o valor "$value"',
    'I see "$label" combo does not contain an option with text of "$text"' : 'Eu vejo que o combo "$label" não contém uma opção com o texto "$text"',
    'I see "$label" combo does not contain an option with value of "$value"' : 'Eu vejo que o combo "$label" não contém uma opção com o valor "$value"',
    'I see "$label" combo has selected value of "$value"' : 'Eu vejo que o valor "$value" está selecionado no combo "$label"',
    'I see "$label" combo has selected text of "$text"' : 'Eu vejo que o texto "$text" está selecionado no combo "$label"',
    'I see "$label" combo does not have a selected option' : 'Eu vejo que o combo "$label" não tem uma opção selecionada',
    
    #scenario
    'I run "$title" scenario of "$story" story' : 'Eu rodo o cenário "$title" da história "$story"',
}