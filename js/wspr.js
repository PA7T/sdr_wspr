/*
 * Red Pitaya SDR WSPR Application
 *
 * Author: Clemens Heese / PA7T <pa7t@wsprlive.net>
 *
 * GPLv3 
 */


(function(WSPR, $, undefined) {
    
    // App configuration
    WSPR.config = {};
    WSPR.config.app_id = 'sdr_wspr';
    WSPR.config.start_app_url = '/bazaar?start=' + WSPR.config.app_id + '?' + location.search.substr(1);
    WSPR.config.stop_app_url = '/bazaar?stop=' + WSPR.config.app_id + '?' + location.search.substr(1);
    WSPR.config.socket_url = 'ws://' + window.location.hostname + ':9002';

    // WebSocket
    WSPR.ws = null;

    // Parameters
    WSPR.processing = false;



    // Starts sdr-wspr application on server
    WSPR.startApp = function() {

        $.get(WSPR.config.start_app_url)
            .done(function(dresult) {
                if (dresult.status == 'OK') {
                    WSPR.connectWebSocket();
                } else if (dresult.status == 'ERROR') {
                    console.log(dresult.reason ? dresult.reason : 'Could not start the application (ERR1)');
                    WSPR.startApp();
                } else {
                    console.log('Could not start the application (ERR2)');
                    WSPR.startApp();
                }
            })
            .fail(function() {
                console.log('Could not start the application (ERR3)');
                WSPR.startApp();
            });
    };
    // Stops sdr-wspr application on server
    WSPR.stopApp = function() {

        $.get(WSPR.config.stop_app_url)
            .done(function(dresult) {
                if (dresult.status == 'OK') {
                    //WSPR.connectWebSocket();
                } else if (dresult.status == 'ERROR') {
                    console.log(dresult.reason ? dresult.reason : 'Could not stop the application (ERR1)');
                    WSPR.stopApp();
                } else {
                    console.log('Could not stop the application (ERR2)');
                    WSPR.stopApp();
                }
            })
            .fail(function() {
                console.log('Could not stop the application (ERR3)');
                WSPR.stopApp();
            });
    };




    WSPR.connectWebSocket = function() {

        //Create WebSocket
        if (window.WebSocket) {
            WSPR.ws = new WebSocket(WSPR.config.socket_url);
            WSPR.ws.binaryType = "arraybuffer";
        } else if (window.MozWebSocket) {
            WSPR.ws = new MozWebSocket(WSPR.config.socket_url);
            WSPR.ws.binaryType = "arraybuffer";
        } else {
            console.log('Browser does not support WebSocket');
        }


        // Define WebSocket event listeners
        if (WSPR.ws) {

            WSPR.ws.onopen = function() {
                $('#hello_message').text("Hello, Red Pitaya!");
                console.log('Socket opened');               
            };

            WSPR.ws.onclose = function() {
                console.log('Socket closed');
            };

            WSPR.ws.onerror = function(ev) {
                $('#hello_message').text("Connection error");
                console.log('Websocket error: ', ev);         
            };

            WSPR.ws.onmessage = function(ev) {
                console.log('Message recieved');
            
                //Capture signals
                if (WSPR.processing) {
                    return;
                }
                WSPR.processing = true;

                try {
                    var data = new Uint8Array(ev.data);
                    var inflate = pako.inflate(data);
                    var text = String.fromCharCode.apply(null, new Uint8Array(inflate));
                    var receive = JSON.parse(text);

                    if (receive.parameters) {
			//console.log('received params')
                        WSPR.processParameters(receive.parameters);

                    }

                    if (receive.signals) {
                        WSPR.processSignals(receive.signals);
                    }
                    WSPR.processing = false;
                } catch (e) {
                    WSPR.processing = false;
                    console.log(e);
                } finally {
                    WSPR.processing = false;
                }
            
            };

        }
    };
    // Processes newly received data for signals
    WSPR.processSignals = function(new_signals) {

        var tmp1;


        // Draw signal
        for (sig_name in new_signals) {

            // Ignore empty parameters
            console.log(new_signals);
            if (new_signals[sig_name].size == 0) continue;

            // Read parameter
            tmp1 = new_signals[par_name].value[0];
            console.log('signal:');
            console.log(new_signals[sig_name]);
            //Update value
            //$('#call').text(tmp1);
            //$('#call').text(parseFloat(voltage).toFixed(2) + "V");
        }
    };

    // Processes newly received data for parameters
    WSPR.processParameters = function(new_parameters) {

        var tmp1;


        // Draw parameters
        for (par_name in new_parameters) {

            // Ignore empty parameters
            if (new_parameters[par_name].size == 0) continue;

            // Read parameter
            tmp1 = new_parameters[par_name].value[0];
            //console.log('size');
            //console.log(new_parameters[par_name]);
            //console.log(new_parameters[par_name].value);

            //Update value
            $('#call').text(tmp1);
            //$('#call').text(parseFloat(voltage).toFixed(2) + "V");
        }
    };

    WSPR.CheckBands = function() {
       var bands_selected = "";
       var i = 0;
       $(":checkbox").each(function () {
           var ischecked = $(this).is(":checked");
           if (ischecked) {
               bands_selected += $(this).val() + "|";
               i++;
               if (i>8) {
                   $(this).prop("checked", false);
               }
           }
       });
       bands_selected = bands_selected.slice(0,-1);
       return bands_selected
    }

    WSPR.CheckServerStatus = function() {
        $.ajax({
                url: '/get_wspr_status',
                type: 'GET',
                timeout: 1500
            })
            .fail(function(msg) {
                if (msg.responseText.split('\n')[0] == "active") {
                    $('#WSPR_RUN').hide();
                    $('#WSPR_STOP').css('display', 'block');
                    $('#label-is-runnung').hide();
                    $('#label-is-not-runnung').show();
                } else {
                    $('#WSPR_STOP').hide();
                    $('#WSPR_RUN').css('display', 'block');
                    $('#label-is-not-runnung').hide();
                    $('#label-is-runnung').show();
                }
            })
    }
    
    WSPR.GetDecodes = function() {
        $.ajax({
                url: '/get_wspr_decodes',
                type: 'GET',
                timeout: 1500
            })
            .fail(function(msg) {
		var decodes = msg.responseText
		dec_lines = decodes.split(/\n/)
		var wsprinfo = "<caption>WSPR spots from last decode</caption>"
		wsprinfo += "<tr><th>Time</th><th>Frequency</th><th>Callsign</th><th>Locator</th><th>SNR / dB</th></tr>";
		for (var i in dec_lines) {
 			wspr_msg = dec_lines[i].split(/\s+/);
			if (wspr_msg.length == 12){
				console.log(wspr_msg)
				wsprinfo += "<tr>";
				wsprinfo += "<td>" + wspr_msg[0] + "</td>"	
				wsprinfo += "<td>" + wspr_msg[5] + "</td>"	
				wsprinfo += "<td>" + wspr_msg[6] + "</td>"	
				wsprinfo += "<td>" + wspr_msg[7] + "</td>"	
				wsprinfo += "<td>" + wspr_msg[3] + "</td>"	
				wsprinfo += "</tr>";
			}
		}
		$("#wspr-decodes-table").html(wsprinfo)	
		//$('#wspr-decodes').val(decodes)
            })
    }
    
    WSPR.GetConfig = function() {
        $.ajax({
                url: '/read_wspr_vars',
                type: 'GET',
                timeout: 1500
            })
            .done(function(msg) {
		$('#call').val(msg.match(/CALL="(.*?)"/)[1]);
		$('#grid').val(msg.match(/GRID="(.*?)"/)[1]);
		$('#comment').val(msg.match(/COMMENT="(.*?)"/)[1]);
		$('#wsprlive-id').val(msg.match(/WLID="(.*?)"/)[1]);
		$('#wsprlive-pass').val(msg.match(/WLPW="(.*?)"/)[1]);
            })
        $.ajax({
                url: '/read_writec2filescfg',
                type: 'GET',
                timeout: 1500
            })
            .done(function(msg) {
		$('#ppm').val(msg.match(/corr = (.*?);\n/)[1]);
		
		//uncheck all frequency boxes
		$(":checkbox").each(function () {
			$(this).prop("checked", false);	
		});
				
		// check frequency boxes that are listed in conf file
		var str2 = ""
		str_freq = msg.split("\n")	
		for (i = 1; i < str_freq.length; i++) { 
			myRegexp = /(?:^|\s)freq = (.*?);(?:\s|$)/g;
			match = myRegexp.exec(str_freq[i])
			if (match !== null){
				str2 = str2.concat("#",match[1].replace('.',''));
				$('#' + match[1].replace('.','')).prop("checked", true);
			}
		}
            })
    }

    WSPR.SetConfig = function() {
        var rc = $('#call').val();
        var rl = $('#grid').val();
        //var c = $('#comment').val().match(/(([A-Za-z0-9-]+).{1,6})/gm);
        var c = $('#comment').val().match(/([A-Za-z0-9-]+)/gm)[0].slice(0,8)
	var ppm = $('#ppm').val();
        var wlid = $('#wsprlive-id').val();
        var wlpw = $('#wsprlive-pass').val();
        var bands = WSPR.CheckBands();
        //$('#wspr-debug').val(bands)
        i=0;
        $(":checkbox").each(function () {
           var ischecked = $(this).is(":checked");
           if (ischecked) {
               i++;
           }
        });
       if (i==8) {
        $.ajax({
                url: '/store_wspr_config?rc="' + rc + '"&rl="' + rl + '"&c="' + c + '"&ppm=' + ppm.replace(',','.') + '&bands=' + bands + '&wlid="' + wlid + '"&wlpw="' + wlpw + '"',
                //url: '/store_wspr_config?rc="' + rc + '"&rl="' + rl + '"&c="' + c + '"&wlid="' + wlid + '"&wlpw="' + wlpw + '"',
                type: 'GET',
                timeout: 1500
            })
            .fail(function(msg) {
                //if (msg.responseText) {$('#wspr-debug').val(msg.responseText)} else {}
            })
        alert('Configuration stored.');
	WSPR.GetConfig();
               }
       else {
        console.log(i);
        alert('Please select exactly 8 bands!');
       }
    }
    
    WSPR.startWSPRserver = function() {
	$.ajax({
                url: '/start_wspr',
                type: 'GET',
                timeout: 5000
            })
            .fail(function(msg) {
                if (msg) {} else {}
            })
    }
    WSPR.stopWSPRserver = function() {
	$.ajax({
                url: '/stop_wspr',
                type: 'GET',
                timeout: 1500
            })
            .fail(function(msg) {
                if (msg.responseText) {} else {}
            })
    }

}(window.WSPR = window.WSPR || {}, jQuery));




// Page onload event handler
$(function() {
    // Start application
    $('#WSPR_RUN').click(WSPR.startWSPRserver);
    $('#WSPR_STOP').click(WSPR.stopWSPRserver);
    $('#a_store').click(WSPR.SetConfig);
    WSPR.GetConfig();

    // monitor if wspr-server is running
    WSPR.CheckServerStatus
    setInterval(WSPR.CheckServerStatus, 1000);
    WSPR.GetDecodes
    setInterval(WSPR.GetDecodes, 1000);

    $(":checkbox").click(WSPR.CheckBands);

   // function to store configuration 
   /*$('#a_store').click(function() {

       // sends configuration to backend
       var local = {};
       local['CALL'] = { value: $('#call').val() };
       local['GRID'] = { value: $('#grid').val() };
       local['COMMENT'] = { value: $('#comment').val() };
       local['PPM'] = { value: $('#ppm').val() };
       local['WLID'] = { value: $('#wsprlive-id').val() };
       local['WLPW'] = { value: $('#wsprlive-pass').val() };
       local['BANDS'] = { value: WSPR.CheckBands() };
       WSPR.ws.send(JSON.stringify({ parameters: local }));
       alert('Configuration stored.');	    
   });*/
    

});
