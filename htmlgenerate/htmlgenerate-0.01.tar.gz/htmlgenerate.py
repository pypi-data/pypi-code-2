# coding: utf-8
# Curso de python Serpro
# Lista: 8 ~ Exercicio: 1
###
# A partir da lista 6 decidimos fazer os exercicios em grupo usando pair programming
###
# Autores: Julio Cesar da S. Pereira , Mateus C. Viegas, Frederico Souza; 

class htmlgenerate:
    def __init__(self):
        self.title=raw_input("Título da página: ")
        self.f=open("index.html","w")
        head=self.head(self.title)
        body=self.body()
        self.f.write("<html>\n")
        self.f.write(head(self.title)
        self.f.write(body())
        self.f.write("</html>")
        self.f.close()
        print "Página criada!"
    def head(self,title):
        return "<head><title>"+title+"</title></head>\n"
    def body(self):
        return "<body>Conteúdo aqui!</body>\n"
    
