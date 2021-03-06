from odoo import models, fields, api
from odoo.exceptions import UserError


class UpdateProjectInfo(models.TransientModel):
    _inherit = 'care_center.base'
    _name = 'update_project_info.wizard'
    _description = 'Let user pick customer & project then add prev customer to followers'

    current_task = fields.Many2one(
        'project.task',
        string='Current Task',
    )
    partner_id = fields.Many2one('res.partner', required=True, string="New Customer")
    new_project = fields.Many2one('project.project', required=True, string="New Project")
    add_follower = fields.Boolean(
        string="Add to followers",
        default=True,
        help="Add current customer to followers so they continue to receive notifications.",
    )

    @api.constrains('current_task', 'new_customer')
    def require_partner_changed(self):
        if not self.current_task or not self.partner_id:
            return

        if self.partner_id == self.current_task.partner_id:
            raise UserError('New Customer is same as old')

    @api.onchange('partner_id')
    def _update_partner_id_domain(self):
        partner = self.partner_id

        if not partner:
            domain = []
        else:
            partner_ids = self.get_partner_ids()
            domain = self.get_partner_domain(partner_ids)

            # Only reset project if the Partner is set, and is
            # NOT related to the current Contact selected
            proj_partner = self.new_project.partner_id and self.new_project.partner_id.id
            if proj_partner and proj_partner not in partner_ids:
                self.new_project = None
        return {
            'domain': {
                'new_project': domain,
            },
        }

    @api.multi
    def update_customer_project(self):
        """
        Update Task to the selected customer & project then
        add prev customer to followers.
        """
        task = self.current_task.with_context({'tracking_disable': True})
        partner = self.current_task.partner_id
        if self.add_follower and partner and partner.email:
            task.message_subscribe([self.current_task.partner_id.id])

        task.write({
            'partner_id': self.partner_id.id,
            'project_id': self.new_project.id,
            'sale_order_id': False,
            'sale_line_id': False,
        })

        so_line = task._default_sale_line_id()
        if so_line:
            task.write({'sale_line_id': so_line})

        return True
