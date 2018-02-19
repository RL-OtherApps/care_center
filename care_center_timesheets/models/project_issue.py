# -*- coding: utf-8 -*-
from odoo import models, api


class ProjectIssue(models.Model):
    _name = 'project.issue'
    _inherit = ['project.utils', 'project.issue']

    @api.multi
    def write(self, vals):
        issue = super(ProjectIssue, self).write(vals)

        if vals.get('partner_id') or vals.get('project_id'):
            self._update_timesheets()

        return issue