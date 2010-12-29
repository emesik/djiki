from creole import Parser
from creole.html_emitter import HtmlEmitter

def render(src):
	doc = Parser(src).parse()
	return HtmlEmitter(doc).emit().encode('utf-8', 'ignore')
