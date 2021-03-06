from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    service_partner = fields.Many2one(
        'res.partner',
        string='Service Partner',
    )
