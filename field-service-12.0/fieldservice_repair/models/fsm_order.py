# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    repair_id = fields.Many2one('repair.order', string='Repair Order')

    @api.model
    def create(self, vals):
        # if FSM order with type repair is created then
        # create a repair order
        order = super(FSMOrder, self).create(vals)
        if order.type.internal_type == 'repair':
            equipment = order.equipment_id
            repair_id = self.env['repair.order'].create({
                'name': order.name or '',
                'category_id': order.category_id.id,
                # 'product_id': equipment.product_id.id or False,
                # 'product_uom': equipment.product_id.uom_id.id or False,
                # 'lot_id': equipment.lot_id.id or '',
                'product_qty': 1,
                'invoice_method': 'none',
                'internal_notes': order.description,
                'guarantee_limit': order.guarantee_limit,
                'product_sn': order.product_sn,
                'Product_color': order.Product_color,
                'Product_production_date': order.Product_production_date,
                'Product_image': order.Product_image,
                'warranty_image': order.warranty_image,
                'plate_image': order.plate_image
            })
            order.repair_id = repair_id
        return order

    @api.multi
    def repair(self):
        repair_id = self.env['repair.order'].create({
            'name': self.name or '',
            'category_id': self.category_id.id,
            'product_qty': 1,
            'invoice_method': 'none',
            'internal_notes': self.description,
            'guarantee_limit': self.guarantee_limit,
            'product_sn': self.product_sn,
            'Product_color': self.Product_color,
            'Product_production_date': self.Product_production_date,
            'Product_image': self.Product_image,
            'warranty_image': self.warranty_image,
            'plate_image': self.plate_image
        })
        self.repair_id = repair_id
