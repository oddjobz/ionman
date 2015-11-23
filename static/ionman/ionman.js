//////////////////////////////////////////////////////////////////////////////
//                                                                          //
//  ionman.js                                                               //
//                                                                          //
//  Refactored  :: 11 Nov 2015                                              //
//  Author      :: Gareth Bult (c) Encryptec Ltd 2015                       //
//  Description :: Common project code                                      //
//                                                                          //
//////////////////////////////////////////////////////////////////////////////

var ionman = ionman || {};

ionman = {

	debug_on      : true,
	realm         : 'ionman',
	port          : '8443',
	connection    : null,
	body_tag      : 'main-content',
	sector        : 'guest',
	sector_sub    : null,
	stack_bottomright : {"dir1": "up", "dir2": "left", "firstpos1": 25, "firstpos2": 25},
	//
	//  function debug() - optionally log to the console
	//
	debug: function(routine,text) {
		if(ionman.debug_on) console.log('['+routine+'] - '+text);
	},

	notify: function(title,text,type,icon) {
		var stack = {"dir1": "up", "dir2": "left", "firstpos1": 100, "firstpos2": 100};
		new PNotify({
			title:   title,
			text:    text,
			type:    type,
			icon:    'glyphicon glyphicon-'+icon,
			addclass:'stack-bottomright',
			stack:   stack
		});
	},

	load : function(target,tag,uri) {

		ionman.debug("load",target+" => "+tag);
		var good = function(data) {
			$('#'+tag).html(data.html);
		};
		var fail = function(data) {
			ionman.debug("load","failed to load object")
			console.log(data);
		};
		ionman.call(target,{'uri':uri},good,fail);
	},

	reset: function() {
		ionman.debug('reset','resetting auth credentials')
		ionman.new_credentials = ionman.credentials;
		ionman.credentials.authid = 'guest';
		ionman.credentials.password = '084e0343a0486ff05530df6c705c8bb4';
		ionman.new_connection = new autobahn.Connection(ionman.new_credentials);
		ionman.new_connection.onopen = ionman.connection_open_replace;
		ionman.new_connection.onclose = ionman.connection_close;
		ionman.new_connection.open();
		$('#button-signout').hide();
		$('#button-signin').show();
	},

	init: function() {
		ionman.debug('init','Initializing ...');
		ionman.credentials = {
			realm        : ionman.realm,
			authmethods  : ["wampcra"],
			url          : 'wss://'+document.location.hostname+':'+ionman.port+'/ws',
			onchallenge  : ionman.wampcra,
			initial_retry_delay : 1.0,
			max_retry_delay  : 10.0,
			retry_delay_growth : 2.0,
			max_retries    : 999999,
			authid : 'guest',
			password : '084e0343a0486ff05530df6c705c8bb4'
		};
		var authid = nss.sessionStorage.get('authid')
		var password = nss.sessionStorage.get('password')
		if( authid && password ) {
			ionman.debug('init','Session is authenticated');
			ionman.credentials.authid = authid;
			ionman.credentials.password = password;
			};
		ionman.connection = new autobahn.Connection(ionman.credentials);
		ionman.connection.onopen = ionman.connection_open;
		ionman.connection.onclose = ionman.connection_close;
		ionman.connection.open();
	},

	connection_open: function(session,details) {
		ionman.debug('open','Session opened');
		nss.sessionStorage.set('authid',ionman.credentials.authid);
        nss.sessionStorage.set('password',ionman.credentials.password);
		ionman.session = session;
		ionman.load('demo.page.render','main-content','welcome.j2.html');
	},

	connection_open_replace: function(session,details) {
		ionman.debug('open','Session opened');
		ionman.connection.close();
		ionman.connection = ionman.new_connection;
		ionman.credentials = ionman.new_credentials;
		nss.sessionStorage.set('authid',ionman.credentials.authid);
        nss.sessionStorage.set('password',ionman.credentials.password);
		ionman.session = session;
        $("#login").fadeOut(300);
        $("body").removeClass("no-scroll");
        if( ionman.credentials.authid != 'guest' ) {
            $('#button-signout').show();
            $('#button-signin').hide();
        }
		ionman.load('demo.page.render','main-content','welcome.j2.html');
	},

	connection_close: function(reason,details) {
		ionman.debug('close','Session closed');
		switch( details.reason ) {
			case 'wamp.goodbye.normal':
				ionman.debug('close','Normal logout');
				break;
			case 'wamp.error.not_authorized':
			case 'wamp.error.authorization_failed':
				ionman.debug('close','Authentication failed');
			default:
				console.log("> Reason: ",reason);
				console.log("> Detail: ",details);
		}
	},

	wampcra: function(session,method,extra) {
		ionman.debug('wampcra','Authenicating');
		return autobahn.auth_cra.sign(ionman.credentials.password,extra.challenge);
	},

	switch_to: function(target) {
		ionman.debug('switch_to',target);
		$.get('/'+target,function(data){
			$('#'+ionman.body_tag).html(data);
		}).fail(function(){
			ionman.debug('switch_to','Unable to acquire page: '+target);
		});
	},

	authenticate: function() {
		ionman.debug('authenticate','Attempting to log in');
		ionman.new_credentials = ionman.credentials;
		ionman.new_credentials.authid = $('[name=login-username]','#login-form').val();
		ionman.new_credentials.password = $.md5($('[name=login-password]','#login-form').val());
		ionman.new_connection = new autobahn.Connection(ionman.new_credentials);
		ionman.new_connection.onopen = ionman.connection_open_replace;
		ionman.new_connection.onclose = ionman.connection_close;
		ionman.new_connection.open();
	},

	call: function(topic,args,success,failure) {
		ionman.session.call(topic,[args],{},{disclose_me:true}).then(success,failure);
	}

};

