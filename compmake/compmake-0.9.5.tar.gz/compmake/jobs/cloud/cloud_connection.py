
import cloud

cloud.setkey(1902, "fcc00f8e8efbfae889be68f74fa13f9507bb3aef")

def hello_cloud():
    return "ciao"

jid = cloud.call(hello_cloud)


print cloud.result(jid)
