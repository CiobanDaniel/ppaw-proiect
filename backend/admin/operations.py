"""Rute MVC pentru configurare, moderare, notificări și analitice."""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request

from .common import (
    VALID_ALERT_TYPES, VALID_REPORT_STATES, get_alerts_accessor, get_analytics_accessor,
    get_notifications_accessor, get_or_404, get_reports_accessor, get_settings_accessor,
    redirect_with_feedback, require_choice, require_present, templates,
)


router = APIRouter()


@router.get('/setari')
def settings_index(request: Request, accessor=Depends(get_settings_accessor)):
    return templates.TemplateResponse(request, 'admin/settings/index.html', {'setari': accessor.get_toate_setarile()})


@router.get('/setari/creare')
def settings_create_get(request: Request):
    return templates.TemplateResponse(request, 'admin/settings/create.html', {})


@router.post('/setari/creare')
def settings_create_post(nume_setare: str = Form(...), valoare_setare: str = Form(...), accessor=Depends(get_settings_accessor)):
    accessor.add_setare(require_present(nume_setare, 'Numele setării'), require_present(valoare_setare, 'Valoarea setării'))
    return redirect_with_feedback('/setari', 'success', 'Setarea a fost creată.')


@router.get('/setari/editare/{setare_id}')
def settings_edit_get(request: Request, setare_id: int, accessor=Depends(get_settings_accessor)):
    setare = get_or_404(accessor.get_setare_by_id(setare_id), 'Setarea')
    return templates.TemplateResponse(request, 'admin/settings/edit.html', {'setare': setare})


@router.post('/setari/editare/{setare_id}')
def settings_edit_post(setare_id: int, nume_setare: str = Form(...), valoare_setare: str = Form(...), accessor=Depends(get_settings_accessor)):
    get_or_404(accessor.update_setare(setare_id, require_present(nume_setare, 'Numele setării'), require_present(valoare_setare, 'Valoarea setării')), 'Setarea')
    return redirect_with_feedback('/setari', 'success', 'Setarea a fost actualizată.')


@router.get('/alerte')
def alerts_index(request: Request, accessor=Depends(get_alerts_accessor)):
    return templates.TemplateResponse(request, 'admin/alerts/index.html', {'alerte': accessor.get_toate_alertele()})


@router.get('/alerte/creare')
def alerts_create_get(request: Request):
    return templates.TemplateResponse(request, 'admin/alerts/create.html', {})


@router.post('/alerte/creare')
def alerts_create_post(mesaj: str = Form(...), tip_alerta: str = Form('info'), accessor=Depends(get_alerts_accessor)):
    accessor.add_alerta(require_present(mesaj, 'Mesajul'), require_choice(tip_alerta, VALID_ALERT_TYPES, 'tipul alertei'))
    return redirect_with_feedback('/alerte', 'success', 'Alerta a fost creată.')


@router.get('/alerte/editare/{alerta_id}')
def alerts_edit_get(request: Request, alerta_id: int, accessor=Depends(get_alerts_accessor)):
    alerta = get_or_404(accessor.get_alerta_by_id(alerta_id), 'Alerta')
    return templates.TemplateResponse(request, 'admin/alerts/edit.html', {'alerta': alerta})


@router.post('/alerte/editare/{alerta_id}')
def alerts_edit_post(alerta_id: int, mesaj: str = Form(...), tip_alerta: str = Form('info'), accessor=Depends(get_alerts_accessor)):
    get_or_404(accessor.update_alerta(alerta_id, require_present(mesaj, 'Mesajul'), require_choice(tip_alerta, VALID_ALERT_TYPES, 'tipul alertei')), 'Alerta')
    return redirect_with_feedback('/alerte', 'success', 'Alerta a fost actualizată.')


@router.get('/rapoarte')
def reports_index(request: Request, accessor=Depends(get_reports_accessor)):
    return templates.TemplateResponse(request, 'admin/reports/index.html', {'rapoarte': accessor.get_toate_rapoartele()})


@router.get('/rapoarte/rezolvare/{rap_id}')
def reports_resolve_get(request: Request, rap_id: int, accessor=Depends(get_reports_accessor)):
    raport = get_or_404(accessor.get_raport_by_id(rap_id), 'Raportul')
    return templates.TemplateResponse(request, 'admin/reports/resolve.html', {'raport': raport, 'admini': accessor.get_admini()})


@router.post('/rapoarte/rezolvare/{rap_id}')
def reports_resolve_post(rap_id: int, stare: str = Form(...), id_admin_rezolvare: int = Form(...), accessor=Depends(get_reports_accessor)):
    require_choice(stare, VALID_REPORT_STATES, 'decizia')
    get_or_404(accessor.rezolva_raport(rap_id, stare, id_admin_rezolvare), 'Raportul')
    return redirect_with_feedback('/rapoarte', 'success', 'Raportul a fost soluționat.')


@router.get('/notificari')
def notifications_index(request: Request, accessor=Depends(get_notifications_accessor)):
    return templates.TemplateResponse(request, 'admin/notifications/index.html', {'notificari': accessor.get_toate_notificarile()})


@router.get('/notificari/creare')
def notifications_create_get(request: Request, accessor=Depends(get_notifications_accessor)):
    return templates.TemplateResponse(request, 'admin/notifications/create.html', {'utilizatori': accessor.get_utilizatori()})


@router.post('/notificari/creare')
def notifications_create_post(id_utilizator: int = Form(...), titlu: str = Form(...), mesaj: str = Form(...), accessor=Depends(get_notifications_accessor)):
    accessor.add_notificare(id_utilizator, require_present(titlu, 'Titlul'), require_present(mesaj, 'Mesajul'))
    return redirect_with_feedback('/notificari', 'success', 'Notificarea a fost trimisă.')


@router.get('/analitice/abonamente')
def analytics_subscriptions(request: Request, accessor=Depends(get_analytics_accessor)):
    return templates.TemplateResponse(request, 'admin/analytics/subscriptions.html', {'abonamente': accessor.get_istoric_abonamente()})


@router.get('/analitice/puncte')
def analytics_points(request: Request, accessor=Depends(get_analytics_accessor)):
    return templates.TemplateResponse(request, 'admin/analytics/points.html', {'tranzactii': accessor.get_tranzactii_puncte()})
