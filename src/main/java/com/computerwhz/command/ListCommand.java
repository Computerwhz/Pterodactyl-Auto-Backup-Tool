package com.computerwhz.command;

import com.computerwhz.Command;
import com.computerwhz.Main;
import com.mattmalec.pterodactyl4j.client.entities.ClientServer;

import java.util.List;

public class ListCommand implements Command {
    @Override
    public void execute(String[] strings) {
        List<ClientServer> servers = Main.getApi().retrieveServers().execute();
        System.out.println("List of available servers");
        for (ClientServer s : servers){
            System.out.println("Name: " + s.getName() + " | ID: " + s.getIdentifier());
        }
        System.out.println("Listed " + servers.size() + " available servers");
    }
}
