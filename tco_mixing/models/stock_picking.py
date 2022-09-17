# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_record_mixing_compound(self):
        if self.state != 'draft':
            raise UserError(_('Use Only draft status'))
        if not self.scheduled_date:
            raise UserError(_('Input "force date1".'))
        if self.picking_type_id.id not in (2, 521): #457
            raise UserError(_('Use Only X1-6103-Manufacturing and X1-6105-Manufacturing'))
        if self.picking_type_id.id == 2:
            self.action_record_mixing_tuico()

        if self.picking_type_id.id == 521:
            self.action_record_mixing_gc()


    def action_record_mixing_tuico(self):
        if self.state != 'draft':
            raise UserError(_('Use Only draft status'))

        rs_data = self.env['tco.getmaterialdetails'].read_group([],
                                                            fields=['materialno', 'weight'], groupby=['materialno'])
        print('=======================================================', rs_data)
        lines = [(5, 0, 0)]
        uom_id = 0
        quantity = 0
        for data in rs_data:
            product_id = self.env['product.template'].read_group([('product_variant_ids.id', '=', data['materialno'][0])], fields=['name','uom_id'], groupby=['name','uom_id'], lazy=False, limit=1)

            for pro in product_id:
                if pro['uom_id'][0]:
                    uom_id = pro['uom_id'][0]
            rs_quantity = self.env['tco.getmaterials'].read_group(
                [("mixingdate", "=", self.scheduled_date), ('getmaterials_ids.materialno', '=', data['materialno'][0])],
                fields=['mixingdate', 'quantity'], groupby=['mixingdate'])
            for qty in rs_quantity:
                if qty['quantity']:
                    quantity = qty['quantity']/qty['mixingdate_count']
            vals = {
                'product_id': data['materialno'],
                'name': data['materialno'][1],
                'product_uom': uom_id,
                'location_id': self.location_id,
                'location_dest_id': self.location_dest_id,
                'product_uom_qty': (data['weight']*quantity),
            }
            lines.append((0, 0, vals))
        print('--------------------------', lines)
        self.move_ids_without_package = lines

    def action_record_mixing_gc(self):
        if self.state != 'draft':
            raise UserError(_('Use Only draft status'))
        rs_data = self.env['tco.getmaterialdetails_gc'].read_group([("getmaterials_id.mixingdate", "=", self.scheduled_date)],
                                                            fields=['materialno', 'weight'], groupby=['materialno'])
        lines = [(5, 0, 0)]
        uom_id = 0
        quantity = 0
        for data in rs_data:
            product_id = self.env['product.template'].read_group([('product_variant_ids.id', '=', data['materialno'][0])], fields=['name','uom_id'], groupby=['name','uom_id'], lazy=False, limit=1)
            for pro in product_id:
                if pro['uom_id'][0]:
                    uom_id=pro['uom_id'][0]
            rs_quantity = self.env['tco.getmaterials_gc'].read_group(
                [("mixingdate", "=", self.scheduled_date), ('getmaterials_ids.materialno', '=', data['materialno'][0])],
                fields=['mixingdate', 'quantity'], groupby=['mixingdate'])
            for qty in rs_quantity:
                if qty['quantity']:
                    quantity = qty['quantity']/qty['mixingdate_count']
            vals = {
                'product_id': data['materialno'],
                'name': data['materialno'][1],
                'product_uom': uom_id,
                'location_id': self.location_id,
                'location_dest_id': self.location_dest_id,
                'product_uom_qty': (data['weight']*quantity),
            }
            lines.append((0, 0, vals))
        self.move_ids_without_package = lines

