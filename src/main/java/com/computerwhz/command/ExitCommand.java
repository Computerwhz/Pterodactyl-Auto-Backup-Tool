package com.computerwhz.command;

import com.computerwhz.Command;
import com.computerwhz.Main;

public class ExitCommand implements Command {
    @Override
    public void execute(String[] args) {
        Main.Exit(0);
    }
}
