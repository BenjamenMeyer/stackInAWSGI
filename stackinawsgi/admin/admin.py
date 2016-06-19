"""
Stack-In-A-WSGI: StackInAWsgiAdmin
"""
import logging

from stackinabox.services.service import StackInABoxService

from stackinawsgi.exceptions import InvalidSessionId


logger = logging.getLogger(__name__)


class StackInAWsgiAdmin(StackInABoxService):
    """
    Stack-In-A-WSGI RESTful Admin API

    :ivar :obj:`StackInAWsgiSessionManager` manager: session manager instance
    :ivar text_type base_uri: base URI for accessing the session to which the
        session uuid will be appended, http://localhost/stackinabox/ which
        would result in http://localhost/stackinabox/<session-id>/
    """

    def __init__(self, session_manager, base_uri):
        """
        Initialize the Admin Interface
        """
        super(StackInAWsgiAdmin, self).__init__('admin')
        self.manager = session_manager
        if base_uri.startswith('/'):
            self.base_uri = base_uri[1:]
        else:
            self.base_uri = base_uri

        if self.base_uri.endswith('/'):
            self.base_uri = self.base_uri[:-1]

        self.register(
            StackInABoxService.DELETE, '/', StackInAWsgiAdmin.remove_session
        )
        self.register(
            StackInABoxService.POST, '/', StackInAWsgiAdmin.create_session
        )
        self.register(
            StackInABoxService.PUT, '/', StackInAWsgiAdmin.reset_session
        )
        self.register(
            StackInABoxService.GET, '/', StackInAWsgiAdmin.get_session_info
        )

    def helper_get_session_id(self, headers):
        """
        Helper to retrieve the session id or build a new one

        :param dict headers: case insensitive header dictionary
        :returns: text_type with the UUID of the session
        """
        session_id = None

        if 'x-session-id' in headers:
            session_id = headers['x-session-id']
        else:
            logger.debug('x-session-id not in headers')

        logger.debug('Found Session Id: {0}'.format(session_id))
        return session_id

    def helper_get_uri(self, session_id):
        """
        Helper to build the session URL

        :param text_type session_id: session-id for URL is for
        :returns: text_type, the URL for the session-id
        """
        logger.debug(
            'Helper Get URI - Base URI: "{0}", Session ID: "{1}"'.format(
                self.base_uri,
                session_id
            )
        )
        return '{0}/{1}/'.format(
            self.base_uri,
            session_id
        )

    def create_session(self, request, uri, headers):
        """
        Create a new session

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            POST /admin/
                X-Session-ID: (Optional) Session-ID to use when creating the
                    new session

        HTTP Responses:
            201 - Session Created
                X-Session-ID header contains the session-id
                Location header contains the URL for the session
        """
        requested_session_id = self.helper_get_session_id(
            headers
        )
        logging.debug(
            'Requested Session Id: {0}'.format(requested_session_id)
        )

        session_id = self.manager.create_session(
            requested_session_id
        )
        logging.debug(
            'Created Session Id: {0}'.format(session_id)
        )

        headers['x-session-id'] = session_id
        headers['location'] = self.helper_get_uri(
            session_id
        )
        return (201, headers, '')

    def remove_session(self, request, uri, headers):
        """
        Remove an existing session

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            DELETE /admin/
                X-Session-ID: (Required) Session-ID to destroy

        HTTP Responses:
            204 - Session Destroyed
            404 - Session-ID Not Found
        """
        try:
            self.manager.remove_session(
                self.helper_get_session_id(
                    headers
                )
            )

        except InvalidSessionId as ex:
            return (404, headers, str(ex))
        else:
            return (204, headers, '')

    def reset_session(self, request, uri, headers):
        """
        Reset the session; shortcut for removing and creating the session
        while preserving the session-id.

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            PUT /admin/
                X-Session-ID: (Required) Session-ID to reset

        HTTP Responses:
            205 - Session Reset
            404 - Session-ID Not Found
        """
        try:
            self.manager.reset_session(
                self.helper_get_session_id(
                    headers
                )
            )

        except InvalidSessionId as ex:
            return (404, headers, str(ex))
        else:
            return (205, headers, '')

    def get_session_info(self, request, uri, headers):
        """
        Get Session Information - TBD

        :param :obj:`Request` request: object containing the HTTP Request
        :param text_type uri: the URI for the request per StackInABox
        :param dict headers: case insensitive header dictionary

        :returns: tuple for StackInABox HTTP Response

        HTTP Request:
            GET /admin/
                X-Session-ID: (Required) Session-ID to reset

        HTTP Responses:
            500 - Not Implemented
        """
        return (500, headers, 'Not Implemented')
