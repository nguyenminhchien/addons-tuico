# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class tco_TaskStagePersonal(models.Model):
    _name = 'tco.task.stage.personal'
    _description = 'Personal Task Stage'
    _table = 'tco_task_user_rel'
    _rec_name = 'stage_id'

    task_id = fields.Many2one('tco.task', required=True, ondelete='cascade', index=True)
    user_id = fields.Many2one('res.users', required=True, ondelete='cascade', index=True)
    stage_id = fields.Many2one('tco.task.type', domain="[('user_id', '=', user_id)]", ondelete='restrict')

    _sql_constraints = [
        ('project_personal_stage_unique', 'UNIQUE (task_id, user_id)', 'A task can only have a single personal stage per user.'),
    ]
