import wx
from logbook import Logger

import eos.db
from service.fit import Fit


pyfalog = Logger(__name__)


class CalcChangeImplantLocationCommand(wx.Command):

    def __init__(self, fitID, source, commit=True):
        wx.Command.__init__(self, True, 'Change Implant Location')
        self.fitID = fitID
        self.source = source
        self.commit = commit
        self.savedSource = None

    def Do(self):
        pyfalog.debug('Doing changing of implant source to {} for fit {}'.format(self.fitID, self.source))
        fit = Fit.getInstance().getFit(self.fitID)
        self.savedSource = fit.implantSource
        if self.source == self.savedSource:
            return False
        fit.implantSource = self.source
        if self.commit:
            eos.db.commit()
        return True

    def Undo(self):
        cmd = CalcChangeImplantLocationCommand(fitID=self.fitID, source=self.savedSource, commit=self.commit)
        return cmd.Do()
