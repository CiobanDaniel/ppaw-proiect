"""Rute MVC pentru abonamente, evenimente, plăți și retrageri."""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request

from .common import (
    AdminValidationError, VALID_WITHDRAWAL_STATES, get_events_accessor, get_levels_accessor,
    get_or_404, get_payments_accessor, get_withdrawals_accessor, parse_form_datetime,
    redirect_with_feedback, require_choice, require_non_negative, require_present, templates,
)


router = APIRouter()


@router.get('/abonamente')
def subscriptions_index(request: Request, accessor=Depends(get_levels_accessor)):
    return templates.TemplateResponse(request, 'admin/subscriptions/index.html', {'nivele': accessor.get_toate_nivelele()})


@router.get('/abonamente/creare')
def subscriptions_create_get(request: Request):
    return templates.TemplateResponse(request, 'admin/subscriptions/create.html', {})


@router.post('/abonamente/creare')
def subscriptions_create_post(nume: str = Form(...), pret_real: float = Form(...), descriere_beneficii: Optional[str] = Form(None), accessor=Depends(get_levels_accessor)):
    require_non_negative(pret_real, 'Prețul')
    accessor.add_nivel(require_present(nume, 'Numele abonamentului'), pret_real, descriere_beneficii)
    return redirect_with_feedback('/abonamente', 'success', 'Nivelul de abonament a fost creat.')


@router.get('/abonamente/editare/{nivel_id}')
def subscriptions_edit_get(request: Request, nivel_id: int, accessor=Depends(get_levels_accessor)):
    nivel = get_or_404(accessor.get_nivel_by_id(nivel_id), 'Nivelul de abonament')
    return templates.TemplateResponse(request, 'admin/subscriptions/edit.html', {'nivel': nivel})


@router.post('/abonamente/editare/{nivel_id}')
def subscriptions_edit_post(nivel_id: int, nume: str = Form(...), pret_real: float = Form(...), descriere_beneficii: Optional[str] = Form(None), accessor=Depends(get_levels_accessor)):
    require_non_negative(pret_real, 'Prețul')
    get_or_404(accessor.update_nivel(nivel_id, require_present(nume, 'Numele abonamentului'), pret_real, descriere_beneficii), 'Nivelul de abonament')
    return redirect_with_feedback('/abonamente', 'success', 'Nivelul de abonament a fost actualizat.')


@router.post('/abonamente/stergere/{nivel_id}')
def subscriptions_delete_post(nivel_id: int, accessor=Depends(get_levels_accessor)):
    get_or_404(accessor.soft_delete(nivel_id), 'Nivelul de abonament')
    return redirect_with_feedback('/abonamente', 'success', 'Nivelul de abonament a fost șters logic.')


def validate_event(recompensa_puncte: int, data_inceput: str, data_sfarsit: str):
    inceput = parse_form_datetime(data_inceput, 'Data de început')
    sfarsit = parse_form_datetime(data_sfarsit, 'Data de sfârșit')
    require_non_negative(recompensa_puncte, 'Recompensa în puncte')
    if sfarsit <= inceput:
        raise AdminValidationError('Data de sfârșit trebuie să fie după data de început.')
    return inceput, sfarsit


@router.get('/evenimente')
def events_index(request: Request, accessor=Depends(get_events_accessor)):
    return templates.TemplateResponse(request, 'admin/events/index.html', {'evenimente': accessor.get_toate_evenimentele()})


@router.get('/evenimente/creare')
def events_create_get(request: Request):
    return templates.TemplateResponse(request, 'admin/events/create.html', {})


@router.post('/evenimente/creare')
def events_create_post(nume: str = Form(...), recompensa_puncte: int = Form(...), data_inceput: str = Form(...), data_sfarsit: str = Form(...), este_activ: Optional[str] = Form(None), accessor=Depends(get_events_accessor)):
    inceput, sfarsit = validate_event(recompensa_puncte, data_inceput, data_sfarsit)
    accessor.add_eveniment(require_present(nume, 'Numele evenimentului'), recompensa_puncte, inceput, sfarsit, este_activ == 'on')
    return redirect_with_feedback('/evenimente', 'success', 'Evenimentul a fost creat.')


@router.get('/evenimente/editare/{ev_id}')
def events_edit_get(request: Request, ev_id: int, accessor=Depends(get_events_accessor)):
    eveniment = get_or_404(accessor.get_eveniment_by_id(ev_id), 'Evenimentul')
    return templates.TemplateResponse(request, 'admin/events/edit.html', {'eveniment': eveniment})


@router.post('/evenimente/editare/{ev_id}')
def events_edit_post(ev_id: int, nume: str = Form(...), recompensa_puncte: int = Form(...), data_inceput: str = Form(...), data_sfarsit: str = Form(...), este_activ: Optional[str] = Form(None), accessor=Depends(get_events_accessor)):
    inceput, sfarsit = validate_event(recompensa_puncte, data_inceput, data_sfarsit)
    get_or_404(accessor.update_eveniment(ev_id, require_present(nume, 'Numele evenimentului'), recompensa_puncte, inceput, sfarsit, este_activ == 'on'), 'Evenimentul')
    return redirect_with_feedback('/evenimente', 'success', 'Evenimentul a fost actualizat.')


@router.post('/evenimente/stergere/{ev_id}')
def events_delete_post(ev_id: int, accessor=Depends(get_events_accessor)):
    get_or_404(accessor.hard_delete(ev_id), 'Evenimentul')
    return redirect_with_feedback('/evenimente', 'success', 'Evenimentul a fost șters definitiv.')


@router.get('/plati')
def payments_index(request: Request, accessor=Depends(get_payments_accessor)):
    return templates.TemplateResponse(request, 'admin/payments/index.html', {'plati': accessor.get_toate_platile()})


@router.get('/plati/rambursare/{plata_id}')
def payments_refund_get(request: Request, plata_id: int, accessor=Depends(get_payments_accessor)):
    plata = get_or_404(accessor.get_plata_by_id(plata_id), 'Plata')
    if plata.stare != 'finalizat':
        raise AdminValidationError('Doar o plată finalizată poate fi rambursată.')
    return templates.TemplateResponse(request, 'admin/payments/refund.html', {'plata': plata, 'admini': accessor.get_admini()})


@router.post('/plati/rambursare/{plata_id}')
def payments_refund_post(plata_id: int, id_admin_rambursare: int = Form(...), motiv_rambursare: str = Form(...), accessor=Depends(get_payments_accessor)):
    get_or_404(accessor.anuleaza_plata_si_servicii(plata_id, id_admin_rambursare, require_present(motiv_rambursare, 'Motivul rambursării')), 'Plata')
    return redirect_with_feedback('/plati', 'success', 'Rambursarea simulată a fost înregistrată.')


@router.get('/cereri-retragere')
def withdrawals_index(request: Request, accessor=Depends(get_withdrawals_accessor)):
    return templates.TemplateResponse(request, 'admin/withdrawals/index.html', {'cereri': accessor.get_toate_cererile()})


@router.get('/cereri-retragere/procesare/{cerere_id}')
def withdrawals_process_get(request: Request, cerere_id: int, accessor=Depends(get_withdrawals_accessor)):
    cerere = get_or_404(accessor.get_cerere_by_id(cerere_id), 'Cererea de retragere')
    if cerere.stare != 'in_asteptare':
        raise AdminValidationError('Această cerere a fost deja procesată.')
    return templates.TemplateResponse(request, 'admin/withdrawals/process.html', {'cerere': cerere, 'admini': accessor.get_admini()})


@router.post('/cereri-retragere/procesare/{cerere_id}')
def withdrawals_process_post(cerere_id: int, stare: str = Form(...), id_admin_procesare: int = Form(...), observatii: Optional[str] = Form(None), accessor=Depends(get_withdrawals_accessor)):
    require_choice(stare, VALID_WITHDRAWAL_STATES, 'decizia')
    get_or_404(accessor.proceseaza_cerere(cerere_id, stare, id_admin_procesare, observatii), 'Cererea de retragere')
    return redirect_with_feedback('/cereri-retragere', 'success', 'Cererea a fost procesată și înregistrată în audit.')
