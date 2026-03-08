package com.computerwhz.command;

import com.computerwhz.Command;

public class HelpCommand implements Command {
    @Override
    public void execute(String[] strings) {
        System.out.println("Commands and usages\n" +
                "\"Backup\" | backup a server | usage: backup <ServerID|all>\n" +
                "\"backupall\" | backup all applicable servers | usage: backupall\n" +
                "\"list\" | lists connected servers | usage: list\n" +
                "\"settimer\" | sets the backup timer | usage: settimer <time(mins)> <Server(all/ServerID)> [repeat(true/false)]\n" +
                "\"canceltimer\" | stops the backup timer | usage canceltimer\n" +
                "\"exit\" | Shutdown this program | usage: exit" );
    }
}
