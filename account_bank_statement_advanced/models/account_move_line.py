# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    move_state = fields.Selection(
        related='move_id.state', string='Move State',
        readonly=True)

    @api.onchange('tax_code_id')
    def _onchange_tax_code(self):
        if self.tax_code_id and self.debit or self.credit:
                self.tax_amount = self.debit or self.credit or False
        else:
            self.tax_amount = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ctx = self._context.copy()
        if ctx.get('act_window_from_bank_statement'):
            if view_type == 'tree':
                view_id = self.env.ref(
                    'account_bank_statement_advanced.'
                    'view_move_line_reconcile_tree').id
                ctx.update({'view_mode': 'tree'})
            elif view_type == 'search':
                view_id = self.env.ref(
                    'account_bank_statement_advanced.'
                    'view_move_line_reconcile_search').id
                ctx.update({'view_mode': 'search'})
        return super(
            AccountMoveLine, self.with_context(ctx)
            ).fields_view_get(view_id=view_id, view_type=view_type,
                              toolbar=toolbar, submenu=submenu)

    @api.multi
    def unlink(self, **kwargs):
        for move_line in self:
            st = move_line.statement_id
            if st and st.state == 'confirm':
                raise UserError(
                    _("Operation not allowed ! "
                      "\nYou cannot delete an Accounting Entry "
                      "that is linked to a Confirmed Bank Statement."))
        return super(AccountMoveLine, self).unlink(**kwargs)

    @api.multi
    def write(self, vals, **kwargs):
        for move_line in self:
            st = move_line.statement_id
            if st and st.state == 'confirm':
                for k in vals:
                    if k not in ['reconcile_id', 'reconcile_partial_id']:
                        raise UserError(
                            _("Operation not allowed ! "
                              "\nYou cannot modify an Accounting Entry "
                              "that is linked to a Confirmed Bank Statement. "
                              "\nStatement = %s"
                              "\nMove = %s (id:%s)\nUpdate Values = %s")
                            % (st.name, move_line.move_id.name,
                               move_line.move_id.id, vals))
        return super(AccountMoveLine, self).write(
            vals, **kwargs)
