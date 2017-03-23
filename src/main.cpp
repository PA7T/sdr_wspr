#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/sysinfo.h>

#include <sstream>

#include "main.h"

/* --------------------------------  OUT PARAMETERS  ------------------------------ */

CStringParameter call("CALL", CBaseParameter::RWSA, "", 10000);
CStringParameter grid("GRID", CBaseParameter::RWSA, "", 10000);
CStringParameter comment("COMMENT", CBaseParameter::RWSA, "", 10000);
CStringParameter wlid("WLID", CBaseParameter::RWSA, "", 10000);
CStringParameter wlpw("WLPW", CBaseParameter::RWSA, "", 10000);
/*
CFloatParameter ppm("PPM", CBaseParameter::RW, 0.0, 0, -100.0, 100.0);
CStringParameter wlid("WSPRLIVE-ID", CBaseParameter::RWSA, "", 10000);
CStringParameter wlpw("WSPRLIVE-PW", CBaseParameter::RWSA, "", 10000);
*/
CStringParameter ppm("PPM", CBaseParameter::RWSA, "", 10000);
CStringParameter bands("BANDS", CBaseParameter::RWSA, "", 10000);

const char *rp_app_desc(void)
{
    return (const char *)"Red Pitaya SDR WSPR 8-channel receiver.\n";
}


int rp_app_init(void)
{
    fprintf(stderr, "Loading sdr_wspr application\n");
//    CDataManager::GetInstance()->SetParamInterval(1000);
    system("/opt/redpitaya/www/apps/sdr_wspr/start.sh");
    return 0;
}


int rp_app_exit(void)
{
    fprintf(stderr, "Unloading sdr_wspr application\n");
    system("/opt/redpitaya/www/apps/sdr_wspr/stop.sh");
    return 0;
}


int rp_set_params(rp_app_params_t *p, int len)
{
    return 0;
}


int rp_get_params(rp_app_params_t **p)
{
    return 0;
}


int rp_get_signals(float ***s, int *sig_num, int *sig_len)
{
    return 0;
}








void UpdateSignals(void){}


void UpdateParams(void){
}


void OnNewParams(void) {
    call.Update();
    grid.Update();
    comment.Update();
    wlid.Update();
    wlpw.Update();
    ppm.Update();
    bands.Update();

    system("mount -o rw,remount /opt/redpitaya");
    
    std::stringstream wsprvars;
    wsprvars << "CALL=\"" << call.Value() << "\"" << '\n';
    wsprvars << "GRID=\"" << grid.Value() << "\"" << '\n';
    wsprvars << "COMMENT=\"" << comment.Value() << "\"" << '\n';
    wsprvars << "WLID=\"" << wlid.Value() << "\"" << '\n';
    wsprvars << "WLPW=\"" << wlpw.Value() << "\"" << '\n';
    std::string command1 = "echo '" + wsprvars.str() + "' > /opt/redpitaya/www/apps/sdr_wspr/wspr-vars.sh";
    system(command1.c_str());

    std::stringstream writec2files;
    
    std::string bands_str = bands.Value();
    std::string delimiter = "|";
    size_t pos = 0;
    std::string token;
    writec2files << "corr = " << ppm.Value() << ";" << '\n';
    writec2files << "bands = (\n";
    size_t i = 0;
    while ((pos = bands_str.find(delimiter)) != std::string::npos) {
        token = bands_str.substr(0, pos);
        bands_str.erase(0, pos + delimiter.length());
	i++;
	if (i==8){
            writec2files << "    \{ freq = " << token << "; chan = 1; \}" << '\n';
    	}
	else{
            writec2files << "    \{ freq = " << token << "; chan = 1; \}," << '\n';
	
	}
    }
    writec2files << ");";


    std::string command2 = "echo '" + writec2files.str() + "' > /opt/redpitaya/www/apps/sdr_wspr/write-c2-files.cfg";
    system(command2.c_str());
    

    //std::string command1 = "echo Helloworld > /tmp/test.txt";
    //call.Value() = "PA7T";
}


void OnNewSignals(void){}


void PostUpdateSignals(void){}
