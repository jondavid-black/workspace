package SDLCPodModel {
    import ScalarValues::*;

    /* Requirements */
    requirement <'R1'> WebAccessible {
        doc /* All tools must have a web-accessible front end. */
    }

    requirement <'R1.1'> ProjectContext {
        doc /* All tools must launch within the shared project directory context. */
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
        part terminal : WebTerminal;
        part storage : PersistentVolume;
        part ingress : IngressController;

        /* Connections for shared storage */
        connect syson.storagePort to storage.accessPort;
        connect penpot.storagePort to storage.accessPort;
        connect vscode.storagePort to storage.accessPort;
        connect opencode.storagePort to storage.accessPort;
        connect terminal.storagePort to storage.accessPort;

        /* Connections for web access */
        connect syson.webPort to ingress.backendPort;
        connect penpot.webPort to ingress.backendPort;
        connect vscode.webPort to ingress.backendPort;
        connect opencode.webPort to ingress.backendPort;
        connect terminal.webPort to ingress.backendPort;
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
        part frontend : PenPotFrontend;
        part backend : PenPotBackend;
        part exporter : PenPotExporter;
        part postgres : PenPotPostgres;
        part valkey : PenPotValkey;
        part mailcatch : PenPotMailcatch;

        port storagePort;
        port webPort;

        connect frontend.storagePort to storagePort;
        connect frontend.webPort to webPort;
        connect backend.dbPort to postgres.dbPort;
        connect backend.cachePort to valkey.cachePort;
        connect backend.smtpPort to mailcatch.smtpPort;
        connect exporter.cachePort to valkey.cachePort;
        
        attribute port : Integer = 8080;
    }

    part def PenPotFrontend {
        port storagePort;
        port webPort;
        attribute image : String = "penpotapp/frontend:latest";
    }

    part def PenPotBackend {
        port dbPort;
        port cachePort;
        port smtpPort;
        attribute image : String = "penpotapp/backend:latest";
    }

    part def PenPotExporter {
        port cachePort;
        attribute image : String = "penpotapp/exporter:latest";
    }

    part def PenPotPostgres {
        port dbPort;
        attribute image : String = "postgres:15";
    }

    part def PenPotValkey {
        port cachePort;
        attribute image : String = "valkey/valkey:8.1";
    }

    part def PenPotMailcatch {
        port smtpPort;
        port webPort;
        attribute image : String = "sj26/mailcatcher:latest";
    }

    part def VSCode {
        port storagePort;
        port webPort;
        attribute port : Integer = 8084;
        attribute ingressPath : String = "/vscode";
    }

    part def OpenCode {
        port storagePort;
        port webPort;
        attribute image : String = "ghcr.io/anomalyco/opencode:latest";
        attribute runtime : String = "Node.js";
        attribute port : Integer = 8083;
        attribute ingressPath : String = "/";
    }

    part def WebTerminal {
        port storagePort;
        port webPort;
        attribute image : String = "tsl0922/ttyd:latest";
        attribute port : Integer = 8085;
        attribute ingressPath : String = "/terminal";
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
