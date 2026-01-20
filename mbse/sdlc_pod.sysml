package SDLCPodModel {
    import ScalarValues::*;

    /* Requirements */
    requirement <'R1'> WebAccessible {
        doc /* All tools must have a web-accessible front end. */
    }

    requirement <'R2'> ScaleToZero {
        doc /* The Pod must scale to zero when not in use. */
    }

    requirement <'R3'> SharedStorage {
        doc /* All containers must share the same persistent volume containing git repositories. */
    }

    requirement <'R4'> SingleUserSupport {
        doc /* The Pod is intended to support a single user. */
    }

    /* System Definition */
    part def SDLCPod {
        part syson : SysON;
        part penpot : PenPot;
        part vscode : VSCode;
        part opencode : OpenCode;
        part storage : PersistentVolume;
        part ingress : IngressController;

        /* Connections for shared storage */
        connect syson.storagePort to storage.accessPort;
        connect penpot.storagePort to storage.accessPort;
        connect vscode.storagePort to storage.accessPort;
        connect opencode.storagePort to storage.accessPort;

        /* Connections for web access */
        connect syson.webPort to ingress.backendPort;
        connect penpot.webPort to ingress.backendPort;
        connect vscode.webPort to ingress.backendPort;
        connect opencode.webPort to ingress.backendPort;
    }

    part def SysON {
        part app : SysONApp;
        part db : SysONDB;
        
        port storagePort;
        port webPort;
        
        connect app.dbPort to db.dbPort;
        connect app.storagePort to storagePort;
        connect app.webPort to webPort;
    }

    part def SysONApp {
        port storagePort;
        port webPort;
        port dbPort;
        attribute image : String = "eclipsesyson/syson:v2025.12.0";
    }

    part def SysONDB {
        port dbPort;
        attribute image : String = "postgres:15";
        attribute port : Integer = 5433;
    }

    part def PenPot {
        port storagePort;
        port webPort;
        attribute url : String;
        attribute ingressPath : String = "/penpot";
    }

    part def VSCode {
        port storagePort;
        port webPort;
        attribute url : String;
        attribute ingressPath : String = "/vscode";
    }

    part def OpenCode {
        port storagePort;
        port webPort;
        attribute url : String;
        attribute ingressPath : String = "/";
    }

    part def IngressController {
        port backendPort;
        port publicPort;
        attribute host : String = "sdlc.local";
    }

    part def PersistentVolume {
        port accessPort;
        attribute mountPath : String = "/data";
    }
}
