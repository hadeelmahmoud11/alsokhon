import itertools,operator
from odoo.addons.web.controllers.main import WebClient, Home
from odoo import http
from odoo.osv import expression
from odoo.http import content_disposition, dispatch_rpc, request
from odoo.addons.http_routing.controllers.main import Routing

class KsRouting(Routing):

    @http.route('/website/translations/<string:unique>', type='http', auth="public", website=True)
    def get_website_translations(self, unique, lang, mods=None):
        IrHttp = request.env['ir.http'].sudo()
        modules = IrHttp.get_translation_frontend_modules()
        mods = [x['name'] for x in request.env['ir.module.module'].sudo().search_read(
            [('state', '=', 'installed')], ['name'])]

        if mods:
            modules += mods
        return WebClient().translations(unique, mods=','.join(modules), lang=lang)