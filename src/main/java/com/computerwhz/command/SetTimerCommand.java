package com.computerwhz.command;

import com.computerwhz.Command;
import com.computerwhz.Main;
import com.mattmalec.pterodactyl4j.client.entities.ClientServer;
import com.mattmalec.pterodactyl4j.client.entities.PteroClient;

public class SetTimerCommand implements Command {

    @Override
    public void execute(String[] args) {

        if (Main.getTimer().isRunning()){
            System.err.println("Timer is already running use command \"canceltimer\" to stop it");
            return;
        }

        if (args.length < 2 || args.length > 3) {
            System.out.println("Usage: settimer <time(mins)> <Server(all/ServerID)> [repeat(true/false)]");
            return;
        }

        try {
            int timeMinutes = Integer.parseInt(args[0]);
            if (timeMinutes <= 0) {
                System.err.println("Time must be greater than 0");
                return;
            }

            boolean repeat = false;
            if (args.length == 3) {
                if (args[2].equalsIgnoreCase("true")) {
                    repeat = true;
                } else if (args[2].equalsIgnoreCase("false")) {
                    repeat = false;
                } else {
                    System.err.println("Could not parse repeat, please input true or false");
                    return;
                }
            }

            ClientServer server = null;
            if (!args[1].equalsIgnoreCase("all")) {
                PteroClient api = Main.getApi();
                server = api.retrieveServerByIdentifier(args[1]).execute();

                if (server == null) {
                    System.err.println("Could not get server, check server ID");
                    return;
                }
            }

            long timeMillis = timeMinutes * 60_000L;
            Main.getTimer().runTimer(timeMillis, repeat, server);
            System.out.println("Timer Set");

        } catch (NumberFormatException e) {
            System.err.println("Could not parse time, please input an integer");
        } catch (Exception e) {
            System.err.println("An error occurred while running the timer: " + e.getMessage());
        }
    }
}