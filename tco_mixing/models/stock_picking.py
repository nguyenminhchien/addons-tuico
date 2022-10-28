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
        if not self.force_date_done:
            raise UserError(_('Input "force date".'))
        if self.picking_type_id.id not in (457, 521): #457, 521
            raise UserError(_('Use Only X1-6103-Manufacturing and X1-6105-Manufacturing'))
        if self.picking_type_id.id == 457:
            self.action_record_mixing_tuico()
        if self.picking_type_id.id == 521:
            self.action_record_mixing_gc()

    def action_record_mixing_tuico(self):
        if self.state != 'draft':
            raise UserError(_('Use Only draft status'))

        docno = self.force_date_done.strftime('%y%m%d')
        self._cr.execute("""Select D.MaterialNo AS ItemNo,pp.default_code, pt.uom_id,round(Sum(D.Weight*H.Quantity)::numeric,2) AS OrderQty 
                        From tco_getmaterials H  
                        Inner Join tco_getmaterialdetails D ON H.id = D.getmaterials_id  
                        inner join product_product pp on D.materialno = pp.id 
                        inner join product_template pt on pp.product_tmpl_id = pt.id 
                        Where H.name = %s 
                        Group By D.MaterialNo, pp.default_code, pt.uom_id """, (docno,))

        lines = [(5, 0, 0)]
        for pid, default_code, uom_id, OrderQty in self._cr.fetchall():
            vals = {
                'product_id': pid,
                'name': default_code,
                'product_uom': uom_id,
                'location_id': self.location_id,
                'location_dest_id': self.location_dest_id,
                'product_uom_qty': OrderQty,
            }
            lines.append((0, 0, vals))
        self.move_ids_without_package = lines


    def action_record_mixing_gc(self):
        if self.state != 'draft':
            raise UserError(_('Use Only draft status'))

        docno = self.force_date_done.strftime('%y%m%d')

        self._cr.execute("""Select D.MaterialNo AS ItemNo,pp.default_code, pt.uom_id,round(Sum(D.Weight*H.Quantity)::numeric,2) AS OrderQty 
                                From tco_getmaterials_gc H  
                                Inner Join tco_getmaterialdetails_gc D ON H.id = D.getmaterials_id  
                                inner join product_product pp on D.materialno = pp.id 
                                inner join product_template pt on pp.product_tmpl_id = pt.id 
                                Where H.name = %s 
                                Group By D.MaterialNo, pp.default_code, pt.uom_id """, (docno,))

        lines = [(5, 0, 0)]
        for pid, default_code, uom_id, OrderQty in self._cr.fetchall():
            vals = {
                'product_id': pid,
                'name': default_code,
                'product_uom': uom_id,
                'location_id': self.location_id,
                'location_dest_id': self.location_dest_id,
                'product_uom_qty': OrderQty,
            }
            lines.append((0, 0, vals))
        self.move_ids_without_package = lines



