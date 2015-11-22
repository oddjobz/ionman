##############################################################################
#   IMPORTS                                                                  #
##############################################################################
from flask          import Flask,send_from_directory,make_response
from jinja2         import Environment,FileSystemLoader
from twisted.python import log
#
##############################################################################
app = Flask(__name__)
##############################################################################
#
JINJA_PATH = '../static/html'
IMAGE_PATH = '../static/images'
JINJA_EXTS = ['jinja2.ext.do',]
#
env = Environment(loader=FileSystemLoader(JINJA_PATH),extensions=JINJA_EXTS)
#
def render_template(template,dictionary,nocache=False):
    """ render a template and dictionary into a response """
    try:
        response = make_response(env.get_template(template).render(dictionary))
        if nocache:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    except:
        log.err()

    return 'Fatal Server Error',500
#
@app.route('/',methods=['GET'])
def index():
    """default page - login prompt?"""
    return render_template('index.html',{},nocache=True)
#
@app.route('/css/<path:path>')
def wsgi_css(path):
    """return static file from given path"""
    return send_from_directory('../static/css',path)
#
@app.route('/js/<path:path>')
def wsgi_js(path):
    """return static file from given path"""
    return send_from_directory('../static/js',path)
#
@app.route('/images/<path:path>')
def wsgi_images(path):
    """return static file from given path"""
    return send_from_directory('../static/images',path)
#
@app.route('/fonts/<path:path>')
def wsgi_fonts(path):
    """return static file from given path"""
    return send_from_directory('../static/fonts',path)
#
@app.route('/favicon.png',methods=['GET'])
def wsgi_favicon():
    """ return the favicon image """
    return send_from_directory('../static/images','favicon.png')
#
@app.route('/html/<path:path>',methods=['GET'])
def wsgi_html(path):
    """ return the favicon image """
    return render_template(path,{},nocache=True)
#
@app.route('/ionman/<path:path>',methods=['GET'])
def wsgi_ionman(path):
    """ return the favicon image """
    return send_from_directory('../static/ionman',path)
#
##############################################################################
