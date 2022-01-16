# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.exceptions import UserError

REQUEST_STATES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('open', 'In progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')]


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    stock_request_ids = fields.One2many('stock.request', 'fsm_order_id',
                                        string="Order Lines")
    request_stage = fields.Selection(REQUEST_STATES, string='Request State',
                                     default='draft', readonly=True,
                                     store=True)
    amount_untaxed = fields.Float('أجمالي المبلغ', compute='_amount_untaxed', store=True)
    amount_tax = fields.Float('Taxes', store=True, readonly=1)
    amount_total = fields.Float('Total', store=True, readonly=1)

    @api.multi
    def action_request_submit(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_('Please create a stock request.'))
            for line in rec.stock_request_ids:
                if line.state == 'draft':
                    if line.order_id:
                        line.order_id.action_submit()
                    else:
                        line.action_submit()
            rec.request_stage = 'submitted'
            print(rec)

    @api.multi
    def action_request_cancel(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_('Please create a stock request.'))
            for line in rec.stock_request_ids:
                if line.state in ('draft', 'submitted'):
                    if line.order_id:
                        line.order_id.action_cancel()
                    else:
                        line.action_cancel()
            rec.request_stage = 'cancel'

    @api.multi
    def action_request_draft(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_('Please create a stock request.'))
            for line in rec.stock_request_ids:
                if line.state == 'cancel':
                    if line.order_id:
                        line.order_id.action_draft()
                    else:
                        line.action_draft()
            rec.request_stage = 'draft'

    @api.onchange('stock_request_ids')
    def _amount_untaxed(self):
        self.amount_untaxed = 0
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_('Please create a stock request.'))
            for line in rec.stock_request_ids:
                self.amount_untaxed += (line.cost * line.product_uom_qty)
        self.write({'amount_untaxed': self.amount_untaxed})
            # rec.amount_untaxed = self.amount_untaxed

    @api.multi
    def action_invoice_create(self):
        InvoiceLine = self.env['account.invoice.line']
        Invoice = self.env['account.invoice']
        invoice = Invoice.create({
            'name': self.name,
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_id.property_account_receivable_id.id
})

        for rec in self:
            for line in rec.stock_request_ids:
                invoice_line = InvoiceLine.create({
                    'invoice_id': invoice.id,
                    'name': self.name,
                    'origin': self.name,
                    'quantity': line.product_uom_qty,
                    'uom_id': line.product_uom_id,
                    'product_id': line.product_id,
                    'price_unit': line.cost,
                    'price_subtotal': 5
                })
