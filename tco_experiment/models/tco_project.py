# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


from odoo.exceptions import UserError

STATUS_COLOR = {
    'on_track': 20,  # green / success
    'at_risk': 2,  # orange
    'off_track': 23,  # red / danger
    'on_hold': 4,  # light blue
    False: 0,  # default grey -- for studio
}

class tco_ProjectTaskType(models.Model):
    _name = 'tco.task.type'
    _description = 'Task Stage'
    _order = 'sequence, id'

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    project_ids = fields.Many2many('tco.project', 'tco_task_type_rel', 'type_id', 'project_id', string='Projects',
        default=_get_default_project_ids)

    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
        help='Override the default value displayed for the blocked state for kanban selection when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready'), translate=True, required=True,
        help='Override the default value displayed for the done state for kanban selection when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
        help='Override the default value displayed for the normal state for kanban selection when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'tco.task')],
        help="If set, an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    rating_template_id = fields.Many2one(
        'mail.template',
        string='Rating Email Template',
        domain=[('model', '=', 'tco.task')],
        help="If set and if the project's rating configuration is 'Rating when changing stage', then an email will be sent to the customer when the task reaches this step.")
    auto_validation_kanban_state = fields.Boolean('Automatic kanban status', default=False,
        help="Automatically modify the kanban state when the customer replies to the feedback for this stage.\n"
            " * Good feedback from the customer will update the kanban state to 'ready for the new stage' (green bullet).\n"
            " * Neutral or bad feedback will set the kanban state to 'blocked' (red bullet).\n")
    is_closed = fields.Boolean('Closing Stage', help="Tasks in this stage are considered as closed.")


    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user, tracking=True)

    def unlink_wizard(self, stage_view=False):
        # self = self.with_context(active_test=False)
        # # retrieves all the projects with a least 1 task in that stage
        # # a task can be in a stage even if the project is not assigned to the stage
        # readgroup = self.with_context(active_test=False).env['tco.task'].read_group([('stage_id', 'in', self.ids)], ['project_id'], ['project_id'])
        # project_ids = list(set([project['project_id'][0] for project in readgroup] + self.project_ids.ids))
        #
        # wizard = self.with_context(project_ids=project_ids).env['tco.task.type.delete.wizard'].create({
        #     'project_ids': project_ids,
        #     'stage_ids': self.ids
        # })
        #
        # context = dict(self.env.context)
        # context['stage_view'] = stage_view
        # return {
        #     'name': _('Delete Stage'),
        #     'view_mode': 'form',
        #     'res_model': 'tco.task.type.delete.wizard',
        #     'views': [(self.env.ref('tco_experiment.view_tco_task_type_delete_wizard').id, 'form')],
        #     'type': 'ir.actions.act_window',
        #     'res_id': wizard.id,
        #     'target': 'new',
        #     'context': context,
        # }
        return {}

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            self.env['tco.task'].search([('stage_id', 'in', self.ids)]).write({'active': False})
        return super(tco_ProjectTaskType, self).write(vals)

class tco_project(models.Model):
    _name = "tco.project"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Project model"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)

    clm_cmpNew = fields.Boolean('New Compound', default=True, tracking=True) #duoc chuyen cmpnew, sau nay xoa di
    cmpnew = fields.Boolean('New Compound', default=True, tracking=True)

    clm_Updatedate = fields.Datetime('Modify Date', default=fields.Datetime.now) #duoc chuyen updatedate, sau nay xoa di
    updatedate = fields.Datetime('Modify Date', default=fields.Datetime.now)

    clm_compound_id = fields.Many2one('tco.compound', 'Compound', required=True, tracking=True)

    clm_descriptionVN = fields.Char('Notes') #duoc chuyen descriptionvn, sau nay xoa di
    descriptionvn = fields.Char('Notes')

    clm_spec_code = fields.Char('Spec Code')
    clm_customer = fields.Char('Customer')
    clm_batchno = fields.Char('Batch No')
    clm_testnumber = fields.Char('Test Number', tracking=True)
    sequence = fields.Integer(string='Sequence', default=1)
    description = fields.Html()

    compound_type = fields.Selection([('AA', 'AA-NR, EPDM'),
                                      ('BA', 'BA-EPDM'),
                                      ('BC', 'BC-CR'),
                                      ('BE', 'BE-CR'),
                                      ('BF', 'BF-NBR'),
                                      ('BG', 'BG-NBR, PU'),
                                      ('BK', 'BK-NBR'),
                                      ('CA', 'CA-EPDM'),
                                      ('CH', 'CH-NBR, PU'),
                                      ('DA', 'DA-EPDM'),
                                      ('DE', 'DE-CM, CSM'),
                                      ('DF', 'DF-AEM(VA), ACM'),
                                      ('DH', 'DH-HNBR, ACM'),
                                      ('EE', 'EE-AEM(VA), ACM'),
                                      ('EH', 'EH-ACM'),
                                      ('FC', 'FC-Silicone'),
                                      ('FE', 'FE-Silicone'),
                                      ('FK', 'FK-Flosilicone'),
                                      ('GE', 'GE-Silicone'),
                                      ('HK', 'HK-FKM, AFlas'),
                                      ], string="1st ASTM Code", required=True, default="GE",
                                     help="Use to get name for lines = [Test Standard][1st ASTM Code][2nd ASTM Code]")

    clm_color = fields.Many2one('product.color', string='Color')

    clm_MaterialCompound = fields.Many2one('product.product', string='Material') # duoc chuyen materialcompound, sau nay xoa di
    materialcompound = fields.Many2one('product.product', string='Material')

    owner_id = fields.Many2one('res.partner', string='Owner')

    clm_compound_ids = fields.Many2many('tco.compound.method', 'Method Request', store=False, tracking=True)

    clm_compound_line_ids = fields.One2many('tco.specific', 'project_id')
    tmp_compound_line_ids = fields.One2many('tco.specific', 'project_id')

    task_ids = fields.One2many('tco.task', 'project_id', string='Tasks')

    produce_ids = fields.One2many('tco.task', 'project_id', string='Tasks', domain=[('clm_produce', '=', 'produce')], tracking=True)

    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def name_get(self):
        result = []
        for res in self:
            name = res.name
            result.append((res.id, name))
        return result

    @api.onchange('clm_compound_ids')
    def _onchange_test(self):
        lines = []
        if self.clm_compound_ids:
            # lines = [(5, 0, 0)]
            lines = []
            existing_line = self.env['tco.compound.method.line'].search([
                ('clm_method_id', 'in', self.clm_compound_ids.ids)
            ])

            for line in existing_line:
                version = None
                year = None
                if line.clm_method_id:
                    if line.clm_method_id.method_title_id.grouptitle == '0':
                        version = line.method_line_ver
                        year = line.method_line_year
                    else:
                        version = line.clm_method_id.method_version
                        year = line.clm_method_id.method_year
                vals = {
                    'clm_method_line_id': line.id,
                    'specific_version': version,
                    'specific_year': year
                }
                lines.append((0, 0, vals))
        self.clm_compound_line_ids = lines


    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the project without removing it.")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['tco.project.stage'].search([], order=order)

    def _default_stage_id(self):
        # Since project stages are order by sequence first, this should fetch the one with the lowest sequence number.
        return self.env['tco.project.stage'].search([], limit=1)

    stage_id = fields.Many2one('tco.project.stage', string='Stage', ondelete='restrict',
                               tracking=True, index=True, copy=False,
                                default = _default_stage_id,
                               group_expand='_read_group_stage_ids')

    label_tasks = fields.Char(string='Use Tasks as', default='Tasks', help="Label used for the tasks of the project.",
                              translate=True)
    color = fields.Integer(string='Color Index')
    partner_id = fields.Many2one('res.partner', string='Customer', auto_join=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    def _compute_task_count(self):
        rs_data = self.env['tco.task'].read_group([('project_id', 'in', self.ids)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in rs_data)
        for rec in self:
            rec.clm_task_count = result.get(rec.id, 0)
    clm_task_count = fields.Integer('Task Count', compute=_compute_task_count)
    def _compute_task_count_true(self):
        rs_data = self.env['tco.task'].read_group([('project_id', 'in', self.ids), ('clm_result', '=', 'ok')], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in rs_data)
        for rec in self:
            rec.clm_task_count_true = result.get(rec.id, 0)
    clm_task_count_true = fields.Integer('Task Count', compute=_compute_task_count_true)
    def _compute_task_count_ng(self):
        rs_data = self.env['tco.task'].read_group([('project_id', 'in', self.ids), ('clm_result', '=', 'ng')], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in rs_data)
        for rec in self:
            rec.clm_task_count_ng = result.get(rec.id, 0)
    clm_task_count_ng = fields.Integer('Task Count', compute=_compute_task_count_ng)
    def _compute_task_count_false(self):
        rs_data = self.env['tco.task'].read_group([('project_id', 'in', self.ids), ('clm_result', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in rs_data)
        for rec in self:
            rec.clm_task_count_false = result.get(rec.id, 0)
    clm_task_count_false = fields.Integer('Task Count', compute=_compute_task_count_false)



    def compute_act_view_task(self):
        if len(self.ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'tco_task_view_search',
                'res_model': 'tco.task',
                'view_mode': 'tree',
                'domain': [('clm_compoundno', '=', self.id)],
            }


    def action_view_tasks(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('tco_experiment.action_view_all_tco_task') \
            .sudo().read()[0]
        action['display_name'] = self.name
        action['domain'] = [('project_id', '=', self.id)]
        # action = self.env["ir.actions.actions"]._for_xml_id("tco_experiment.act_tco_project_2_tco_task_all")
        return action
    def action_view_tasks_ng(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('tco_experiment.action_view_all_tco_task') \
            .sudo().read()[0]
        action['display_name'] = self.name
        action['domain'] = [('project_id', '=', self.id), ('clm_result', '=', 'ng')]
        # action = self.env["ir.actions.actions"]._for_xml_id("tco_experiment.act_tco_project_2_tco_task_all")
        return action
    def action_view_tasks_ok(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('tco_experiment.action_view_all_tco_task') \
            .sudo().read()[0]
        action['display_name'] = self.name
        action['domain'] = [('project_id', '=', self.id), ('clm_result', '=', 'ok')]
        # action = self.env["ir.actions.actions"]._for_xml_id("tco_experiment.act_tco_project_2_tco_task_all")
        return action
    def action_view_tasks_false(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('tco_experiment.action_view_all_tco_task') \
            .sudo().read()[0]
        action['display_name'] = self.name
        action['domain'] = [('project_id', '=', self.id), ('clm_result', '=', False)]
        # action = self.env["ir.actions.actions"]._for_xml_id("tco_experiment.act_tco_project_2_tco_task_all")
        return action
    def action_view_tasks_produce(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('tco_experiment.action_view_all_tco_task') \
            .sudo().read()[0]
        action['display_name'] = self.name
        action['domain'] = [('project_id', '=', self.id), ('clm_produce', '=', 'produce')]
        # action = self.env["ir.actions.actions"]._for_xml_id("tco_experiment.act_tco_project_2_tco_task_all")
        return action


    def action_view_kanban_project(self):
        # [XBO] TODO: remove me in master
        return

    @api.model
    def _action_open_all_projects(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'tco_experiment.open_view_project_all_group_stage')
        return action

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('clm_compound_id', operator, name)]
        model_ids = self._search((domain + args), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid)) #odoo V13
        # return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid) #odoo 15

    def unlink(self):
        if self.env['tco.task'].search([('project_id', 'in', self.ids)], limit=1):
            raise UserError(_('Used by Task.'))
        return super(tco_project, self).unlink()

class tco_ProjectStage(models.Model):
    _name = 'tco.project.stage'
    _description = 'Project Stage'
    _order = 'sequence, id'

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=50)
    name = fields.Char(required=True, translate=True)

    fold = fields.Boolean('Folded in Kanban', help="This stage is folded in the kanban view.")
