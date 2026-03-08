package com.computerwhz;

import com.mattmalec.pterodactyl4j.client.entities.Backup;
import com.mattmalec.pterodactyl4j.client.entities.ClientServer;
import com.mattmalec.pterodactyl4j.client.entities.PteroClient;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class BackupManager {

    private final PteroClient api;

    public BackupManager(PteroClient api){ this.api = api; }

    public void BackUpAll(){
       List<ClientServer> servers = api.retrieveServers().all().execute();
       for (ClientServer s : servers){
           BackUp(s);
       }
    }

    public void BackUp(ClientServer backupServer){
        if (backupServer.isSuspended()){
            System.err.println("Server is Suspended");
            return;
        }
        if (backupServer.isInstalling()) {
            System.err.println("Server is Installing");
        }
        if (backupServer.isTransferring()) {
            System.err.println("Server is Transferring");
        }

        int maxBackups = Integer.parseInt(backupServer.getFeatureLimits().getBackups());
        List<Backup> backups = new ArrayList<>(backupServer.retrieveBackups().all().execute());
        backups.sort(Comparator.comparing(Backup::getTimeCompleted));
        if (maxBackups > 0) {
            if (backups.size() >= maxBackups) {
                Backup oldestBackup = backups.stream()
                        .filter(b -> !b.isLocked())
                        .findFirst()
                        .orElse(null);

                if (oldestBackup != null) {
                    System.out.println("Deleting oldest unlocked backup: " + oldestBackup.getName() + " On server " + backupServer.getName() + " (" + backupServer.getIdentifier() + ")" );
                    oldestBackup.delete().execute();

                } else {
                    System.out.println("All backups are locked, cannot delete any! Skipping server " + backupServer.getName() + " (" + backupServer.getIdentifier() + ")" );
                    return;
                }
            }
                Backup b = backupServer.getBackupManager().createBackup().setName("Auto Backup tool at " + System.currentTimeMillis()).execute();
                System.out.println("Created new backup" + b.getName() + " On server " + backupServer.getName() + " (" + backupServer.getIdentifier() + ")");

        }
        else {
            System.out.println("Backups disabled skipping server " + backupServer.getName() + " (" + backupServer.getIdentifier() + ")" );
        }
    }
}
