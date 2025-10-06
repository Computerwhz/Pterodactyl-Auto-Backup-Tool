package com.computerwhz;

import com.mattmalec.pterodactyl4j.PteroBuilder;
import com.mattmalec.pterodactyl4j.client.entities.PteroClient;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {

    private static String panelUrl;
    private static String apiKey;
    private static PteroClient api;
    private static BackupManager backupManager;

    public static void main(String[] args) {

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--panelurl") && i + 1 < args.length){
                panelUrl = args[i + 1];
            }
            if (args[i].equals("--apikey") && i + 1 < args.length) {
                apiKey = args[i + 1];
            }
        }

        try{
            api = PteroBuilder.createClient(panelUrl, apiKey);
            System.out.println("Connected to the panel successfully");
        } catch (Exception e) {
            System.err.println("Panel Connection failed" + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }

        backupManager = new BackupManager(getApi());
    }

    public static BackupManager getBackupManager(){
        return backupManager;
    }

    public static PteroClient getApi() {
        return api;
    }
}