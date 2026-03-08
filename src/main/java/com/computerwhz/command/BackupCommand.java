package com.computerwhz.command;

import com.computerwhz.BackupManager;
import com.computerwhz.Command;
import com.computerwhz.Main;
import com.mattmalec.pterodactyl4j.client.entities.ClientServer;
import com.mattmalec.pterodactyl4j.client.entities.PteroClient;

import java.util.List;

public class BackupCommand implements Command {
    @Override
    public void execute(String[] args) {
        String arg = args[0];
        if (arg.equals("all")){
            Main.getBackupManager().BackUpAll();
        }
        else{
            PteroClient api = Main.getApi();

            ClientServer server = api.retrieveServerByIdentifier(arg).execute();
            if (server == null){
                System.err.println("Could not get server check server ID");
                return;
            }

            Main.getBackupManager().BackUp(server);
        }
    }


}
