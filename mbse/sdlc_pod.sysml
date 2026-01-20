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

        /* Connections for shared storage */
        connect syson.storagePort to storage.accessPort;
        connect penpot.storagePort to storage.accessPort;
        connect vscode.storagePort to storage.accessPort;
        connect opencode.storagePort to storage.accessPort;
    }

    part def SysON {
        port storagePort;
        attribute url : String;
    }

    part def PenPot {
        port storagePort;
        attribute url : String;
    }

    part def VSCode {
        port storagePort;
        attribute url : String;
    }

    part def OpenCode {
        port storagePort;
        attribute url : String;
    }

    part def PersistentVolume {
        port accessPort;
        attribute mountPath : String = "/data";
    }
}
