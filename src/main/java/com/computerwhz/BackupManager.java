package com.computerwhz;

import com.mattmalec.pterodactyl4j.client.entities.Backup;
import com.mattmalec.pterodactyl4j.client.entities.ClientServer;
import com.mattmalec.pterodactyl4j.client.entities.PteroClient;

import java.util.Comparator;
import java.util.List;

public class BackupManager {

    private PteroClient api;

    public BackupManager(PteroClient api){ this.api = api; }

    public void BackUpAll(){
       List<ClientServer> servers = api.retrieveServers().all().execute();
       for (ClientServer s : servers){
           int maxBackups = Integer.parseInt(s.getFeatureLimits().getBackups());
           List<Backup> backups = s.retrieveBackups().all().execute();
           backups.sort(Comparator.comparing(Backup::getTimeCompleted));
           if (maxBackups > 0 ){
               if (backups.size() >= maxBackups) {
                   Backup oldestBackup = backups.stream()
                           .filter(b -> !b.isLocked())
                           .findFirst()
                           .orElse(null);

                   if (oldestBackup != null) {
                       System.out.println("Deleting oldest unlocked backup: " + oldestBackup.getName() + " On server " + s.getName() + " (" + s.getIdentifier() + ")" );
                       oldestBackup.delete().execute();

                   } else {
                       System.out.println("All backups are locked, cannot delete any! Skipping on server " + s.getName() + " (" + s.getIdentifier() + ")" );
                   }

                   Backup b = s.getBackupManager().createBackup().setName("Backup Created by Auto Backup tool at " + System.currentTimeMillis()).execute();
                   System.out.println("Created new backup" + b.getName() + " On server " + s.getName() + " (" + s.getIdentifier() + ")");
               }
           }
           else {
               System.out.println("Backups disabled skipping on server " + s.getName() + " (" + s.getIdentifier() + ")" );
           }
       }
    }


}
