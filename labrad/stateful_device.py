# Copyright (C) 2015  Chris Macklin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class StatefulDeviceServerWrapper(object):
    """A wrapper class to provide locally-defined state for Device servers.

    Wrapping a DeviceServer in this class ensures that select_device is called
    automatically before any server call, eliminating bugs related to potentially
    unknown server state.
    """

    def __init__(self, server, device):
        """Wrap a server to refer only to a particular device.

        Args:
            server: the ServerWrapper to wrap.  This server must have a
                select_device attribute.
            device (str or int): the device to control using this wrapper.  The
                validity of the device is not checked until a call to the server
                is made.

        Raises:
            NotADeviceServerError if the provided server does not have a
                selectDevice attribute.
        """
        if not hasattr(server, 'select_device'):
            raise NotADeviceServerError("The provided server does not have a"
                                        " select_device attribute.")
        self._server = server
        self._device = device

    def select_device(self, device):
        self._device = device

    def __getattr__(self, attr):

        if not hasattr(self._server, attr):
            return None

        self._server.select_device(self._device)
        return getattr(self._server, attr)

    def __dir__(self):
        return dir(self._server)

    def __repr__(self):
        return ("Stateful wrapper for device '{}' for:\n".format(self._device) +
                repr(self._server))

class NotADeviceServerError(Exception):
    """Error to indicate a server is not a DeviceServer."""
    pass