# -*- coding: utf-8 -*-
from datetime import datetime
from time import strptime

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

class tco_task(models.Model):
    _name = "tco.task"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Taks model"
    _rec_name = 'name'

    name = fields.Char(string='Test Number', required=True, readonly=False, index=True, store=True, default=lambda self: _('New'), tracking=True)
    display_name = fields.Char(store=True, help="Use only show data")

    clm_Updatedate = fields.Datetime('Modify Date', related='project_id.updatedate') # duoc chuyen updatedate, sau nay xoa di
    updatedate = fields.Datetime('Modify Date', related='project_id.updatedate')

    clm_color = fields.Many2one('product.color', string='Color', related='project_id.clm_color')

    clm_MaterialCompound = fields.Many2one('product.product', string='Material', related='project_id.materialcompound') # duoc chuyen updatedate, sau nay xoa di
    materialcompound = fields.Many2one('product.product', string='Material',
                                           related='project_id.materialcompound')

    clm_testdate = fields.Date(string='Test Date', required=True, readonly=False, index=True, copy=False,
                                 default=fields.Datetime.now, tracking=True)
    clm_issualno = fields.Integer("Issual No", default=1, tracking=True)

    clm_descriptionVN = fields.Char('DescriptionVN') # duoc chuyen descriptionvn, sau nay xoa di
    descriptionvn = fields.Char('DescriptionVN')

    description = fields.Html()
    clm_specific = fields.Char('Specific Value')

    clm_result = fields.Selection([('ok', 'OK'), ('ng', 'NG')], string="Result", tracking=True)
    clm_produce = fields.Selection([('produce', 'PRODUCE')], string="Produce", tracking=True)

    owner_id = fields.Many2one('res.partner', string='Owner')
    press_post_id = fields.One2many('tco.press.post', 'task_id', string='Press Post Cure')

    compoundas_ids = fields.One2many('tco.compoundas', 'task_id', string='Formula A')
    project_id = fields.Many2one('tco.project', string='Project', required=True, store=True,
                                 ondelete='cascade')

    project_new = fields.Boolean(related="project_id.cmpnew", store=True)

    clm_compound_id = fields.Char(string="Compound", related="project_id.clm_compound_id.name", store=True)
    user_ids = fields.Many2many('res.users', relation='tco_task_user_rel', column1='task_id', column2='user_id',
                                string='Assignees', default=lambda self: not self.env.user.share and self.env.user,
                                context={'active_test': False}, tracking=True)

    parent_id = fields.Many2one('tco.task', string='Parent Task', index=True)
    color = fields.Integer(string='Color Index')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True, string="Starred", tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(string='Sequence', index=True, default=1,
                              help="Gives the sequence order when displaying a list of tasks.")
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Status',
        copy=False, default='normal', required=True)

    clm_method_line_ids = fields.One2many("tco.result", 'task_id', string="Method", tracking=True)
    clm_compound_line_id = fields.One2many('tco.result', 'task_id', string="Method Line", copy=False , tracking=True)
    clm_testing_ids = fields.One2many("tco.testing", 'task_id', string="Testing Sample", tracking=True)
    clm_mooney_ids = fields.One2many("tco.mooney", 'task_id', string="Mooney", tracking=True)

    # rheometer
    clm_Temp = fields.Float('Temp')
    clm_ML = fields.Float('ML')
    clm_MH = fields.Float('MH')
    clm_TS1 = fields.Char('TS1')
    clm_TS2 = fields.Char('TS2')
    clm_TC50 = fields.Char('TC50')
    clm_TC90 = fields.Char('TC90')

    @api.onchange('project_id')
    def _onchange_project(self):
        lines = [(5, 0, 0)]
        existing_line = self.env['tco.specific'].search([
            ('project_id', 'in', self.project_id.ids)
        ])
        for line in existing_line:
            vals = {
                'clm_method_line_id': line.id
            }
            lines.append((0, 0, vals))
        self.clm_compound_line_id = lines


    @api.onchange('clm_result')
    def _onchange_test(self):
        for task in self:
            if task.clm_result == 'ok':
                task.kanban_state = 'done'

    @api.model
    def default_get(self, fields):
        res = super(tco_task, self).default_get(fields)
        if 'project_id' in fields:
            res['project_id'] = self._context.get('active_id', False)
        return res

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.depends('project_id')
    def _compute_stage_id(self):
        for task in self:
            if task.project_id:
                if task.project_id not in task.stage_id.project_ids:
                    task.stage_id = task.stage_find(task.project_id.id, [
                        ('fold', '=', False), ('is_closed', '=', False)])
            else:
                task.stage_id = False

    stage_id = fields.Many2one('tco.task.type', string='Stage', compute=_compute_stage_id,
                               store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                               domain="[('project_ids', '=', project_id)]", copy=False, task_dependency_tracking=True)



    @api.model
    def _read_group_type_ids(self, stages, domain, order):
        return self.env['tco.task.type'].search([], order=order)
    def _default_type_id(self):
        # Since project stages are order by sequence first, this should fetch the one with the lowest sequence number.
        return self.env['tco.task.type'].search([], limit=1)
    personal_stage_type_id = fields.Many2one('tco.task.type', string='Personal User Stage', store=True,
                                             help="The current user's personal task type.",
                                             default=_default_type_id,
                                             group_expand='_read_group_type_ids', tracking=True)

    display_project_id = fields.Many2one('tco.project', index=True)

    def name_get(self):
        result = []
        for res in self:
            name = '%s Ver: %s'% (res.name, res.clm_issualno)
            result.append((res.id, name))
        return result

    @api.model
    def create(self, vals):
        name = None
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = datetime.strftime(fields.Datetime.now(), "%y%m%d") + '-' + self.env['ir.sequence'].next_by_code('tco.task') or _('New')

        if self.name or vals.get('name'):
            name = "%s%s" % (name, vals.get('name') or self.name)
        if self.clm_issualno:
            name = "%s Ver: %s" % (name, self.clm_issualno)
        vals['display_name'] = name
        return super(tco_task, self).create(vals)

    def write(self, vals):
        name = None
        if self.name or vals.get('name'):
            name = "%s%s" % (name, vals.get('name') or self.name)
        if self.clm_issualno:
            name = "%s Ver: %s" % (name, self.clm_issualno)
        vals['display_name'] = name

        return super(tco_task, self).write(vals)


    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    # def action_view_testing(self):
    #     action = self.with_context(active_id=self.id, active_ids=self.ids) \
    #         .env.ref('tco_experiment.open_view_testing_all') \
    #         .sudo().read()[0]
    #     action['display_name'] = self.name
    #     action['domain'] = [('task_id', '=', self.id)]
    #     # action = self.env["ir.actions.actions"]._for_xml_id("tco_experiment.act_tco_project_2_tco_task_all")
    #     return action

class tco_mooney(models.Model):
    _name = 'tco.mooney'
    _description = "Mooney"

    name = fields.Char('name')
    sequence = fields.Integer(string='Sequence', default=1)

    clm_testmode = fields.Char('Test Mode')
    clm_temp = fields.Float('Temp')
    clm_ml = fields.Float('ML')
    clm_mf = fields.Float('MF')
    clm_ts5 = fields.Char('TS5')
    clm_ts45 = fields.Char('TS45')


    clm_result = fields.Selection([('ok', 'OK'), ('ng', 'NG')], string="Result", default='ok')

    task_id = fields.Many2one('tco.task', string='Task')
    project_id = fields.Many2one('tco.project', related="task_id.project_id", store=True,
                                 help="Use only get Method Request tco_specific in project")

    product_type = fields.Selection([
                    ('material', 'Material'),
                    ('compound', 'Compound'),
                    ], string='product_type',
                    copy=True, required=True, store=True)
    lot = fields.Char('Lot')
    compound_id = fields.Many2one('tco.compound', related="project_id.clm_compound_id", store=True, string='Material')

    product_id = fields.Many2one('product.product', string='Material')

    @api.model
    def create(self, vals):
        name = None

        vals['name'] = datetime.strftime(fields.Datetime.now(), "%y%m%d") + '-' + self.env[
            'ir.sequence'].next_by_code('tco.task') or _('New')

        if self.name or vals.get('name'):
            name = "%s%s" % (name, vals.get('name') or self.name)
        if self.clm_issualno:
            name = "%s Ver: %s" % (name, self.clm_issualno)
        vals['display_name'] = name
        return super(tco_task, self).create(vals)





