import math

import wx

import eos.db
import gui.mainFrame
from gui import globalEvents as GE
from gui.fitCommands.calc.drone.projectedAdd import CalcAddProjectedDroneCommand
from gui.fitCommands.calc.drone.projectedRemove import CalcRemoveProjectedDroneCommand
from gui.fitCommands.helpers import DroneInfo, InternalCommandHistory
from service.fit import Fit


class GuiChangeProjectedDroneMetasCommand(wx.Command):

    def __init__(self, fitID, itemIDs, newItemID):
        wx.Command.__init__(self, True, 'Change Projected Drone Metas')
        self.internalHistory = InternalCommandHistory()
        self.fitID = fitID
        self.itemIDs = itemIDs
        self.newItemID = newItemID

    def Do(self):
        sFit = Fit.getInstance()
        fit = sFit.getFit(self.fitID)
        results = []
        for itemID in self.itemIDs:
            drone = next((pd for pd in fit.projectedDrones if pd.itemID == itemID), None)
            if drone is None:
                continue
            if drone.itemID == self.newItemID:
                continue
            info = DroneInfo.fromDrone(drone)
            info.itemID = self.newItemID
            cmdRemove = CalcRemoveProjectedDroneCommand(fitID=self.fitID, itemID=itemID, amount=math.inf, commit=False)
            cmdAdd = CalcAddProjectedDroneCommand(fitID=self.fitID, droneInfo=info, commit=False)
            results.append(self.internalHistory.submitBatch(cmdRemove, cmdAdd))
        success = any(results)
        eos.db.commit()
        sFit.recalc(fit)
        wx.PostEvent(gui.mainFrame.MainFrame.getInstance(), GE.FitChanged(fitID=self.fitID))
        return success

    def Undo(self):
        success = self.internalHistory.undoAll()
        eos.db.commit()
        Fit.getInstance().recalc(self.fitID)
        wx.PostEvent(gui.mainFrame.MainFrame.getInstance(), GE.FitChanged(fitID=self.fitID))
        return success
