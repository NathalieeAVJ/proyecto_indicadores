import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { formatDate } from './format';
import api from '@/services/api';

// Shared Helper to load image
const loadImage = (url) => {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => resolve(null);
        img.src = url;
    });
};

/**
 * Global PDF Reporting Engine for NatTelf
 * handles Cover Pages, Letterheads, Logo, and Author info.
 */
export const generatePDFReport = async ({ title, subtitle, headers, body, filename, metadata, author }) => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    const logo = await loadImage('/logo.png');

    // --- 1. COVER PAGE ---
    // Background Accents
    doc.setFillColor(149, 117, 205); // NatTelf Purple
    doc.rect(0, 0, pageWidth, 50, 'F');
    
    if (logo) {
        doc.addImage(logo, 'PNG', pageWidth / 2 - 15, 8, 30, 30);
    }
    
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(22);
    doc.text('NatTelf', pageWidth / 2, 45, { align: 'center' });
    
    // Main Title
    doc.setTextColor(40, 40, 40);
    doc.setFontSize(28);
    doc.text(title, pageWidth / 2, 100, { align: 'center' });
    
    // Subtitle / Scope
    if (subtitle) {
        doc.setFontSize(16);
        doc.setTextColor(100);
        doc.text(subtitle, pageWidth / 2, 115, { align: 'center' });
    }

    // Report Details
    doc.setDrawColor(200);
    doc.line(40, 140, pageWidth - 40, 140);
    
    doc.setFontSize(11);
    doc.setTextColor(80);
    const detailsY = 160;
    doc.text(`Fecha de Emisión: ${formatDate(new Date())}`, pageWidth / 2, detailsY, { align: 'center' });
    doc.text(`Generado en: Caracas, Venezuela`, pageWidth / 2, detailsY + 8, { align: 'center' });
    
    if (author) {
        doc.setFontSize(12);
        doc.setTextColor(50);
        doc.text(`Exportado por: ${author}`, pageWidth / 2, detailsY + 20, { align: 'center' });
    }

    if (metadata) {
        let currentY = detailsY + 35;
        doc.setFontSize(10);
        Object.entries(metadata).forEach(([key, value]) => {
            doc.text(`${key}: ${value}`, pageWidth / 2, currentY, { align: 'center' });
            currentY += 8;
        });
    }

    // Footer of cover
    doc.setFillColor(245, 245, 245);
    doc.rect(0, pageHeight - 30, pageWidth, 30, 'F');
    doc.setFontSize(9);
    doc.setTextColor(150);
    doc.text('© 2026 NatTelf - Sistema de Gestión de Indicadores y Operaciones de Red', pageWidth / 2, pageHeight - 15, { align: 'center' });

    // --- 2. DATA PAGE ---
    doc.addPage();
    doc.setFillColor(149, 117, 205);
    doc.rect(10, 10, 5, 20, 'F'); 
    doc.setTextColor(40);
    doc.setFontSize(18);
    doc.text('NatTelf', 20, 20);
    doc.setFontSize(9);
    doc.setTextColor(100);
    doc.text(`REPORTE DETALLADO: ${title.toUpperCase()}`, 20, 26);
    
    doc.text(formatDate(new Date()), pageWidth - 60, 20);
    doc.line(10, 35, pageWidth - 10, 35);

    autoTable(doc, {
        startY: 45,
        head: [headers],
        body: body,
        theme: 'striped',
        headStyles: { 
            fillColor: [149, 117, 205], 
            textColor: 255, 
            fontSize: 10,
            halign: 'center'
        },
        bodyStyles: { fontSize: 9 },
        alternateRowStyles: { fillColor: [248, 243, 252] },
        margin: { top: 40 },
        didDrawPage: function(data) {
            doc.setFontSize(8);
            doc.text(`Página ${doc.internal.getNumberOfPages()}`, data.settings.margin.left, pageHeight - 10);
        }
    });

    // Finalize File
    const finalFilename = filename || `nattelf_report_${Date.now()}.pdf`;
    doc.save(finalFilename);

    // LOGGING TO SYSTEM
    try {
        await api.post('audit-logs/create_manual/', {
            action: 'other',
            module: 'Reportes',
            description: `Exportación de PDF: ${title}. Archivo: ${finalFilename}`
        });
    } catch (e) {
        console.error('Audit failed for export', e);
    }
};

/**
 * Generates a formal Employment Verification Letter (Constancia de Trabajo)
 */
export const generateWorkLetter = async (employee) => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const logo = await loadImage('/logo.png');
    const signature = await loadImage('/signature.png');

    // Header
    doc.setFillColor(149, 117, 205);
    doc.rect(0, 0, pageWidth, 40, 'F');
    
    if (logo) {
        doc.addImage(logo, 'PNG', 15, 8, 25, 25);
    }
    
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.text('NatTelf', 45, 25);
    
    doc.setTextColor(40);
    doc.setFontSize(22);
    doc.text('CONSTANCIA DE TRABAJO', pageWidth / 2, 60, { align: 'center' });
    
    doc.setFontSize(12);
    const dateStr = formatDate(new Date());
    doc.text(`Caracas, ${dateStr}`, pageWidth - 20, 80, { align: 'right' });
    
    const bodyText = `
    Por medio de la presente, la empresa NatTelf C.A. hace constar que el ciudadano(a) ${employee.first_name} ${employee.last_name}, titular de la Cédula de Identidad ${employee.dni}, labora en nuestra institución desde el ${employee.hire_date}.
    
    Actualmente desempeña el cargo de ${employee.position} en el departamento de ${employee.department}, percibiendo un sueldo base mensual de $${parseFloat(employee.base_salary).toLocaleString()}.
    
    Esta constancia se emite a petición del interesado para los fines legales que considere convenientes.
    `;
    
    doc.setFont('helvetica', 'normal');
    const splitText = doc.splitTextToSize(bodyText.trim(), 170);
    doc.text(splitText, 20, 100);
    
    // Digital Signature
    const sigY = 200;
    if (signature) {
        doc.addImage(signature, 'PNG', pageWidth / 2 - 25, sigY - 25, 50, 20);
    }
    doc.line(60, sigY, 150, sigY);
    doc.setFontSize(10);
    doc.text('Nathaliee Vargas', pageWidth / 2, sigY + 5, { align: 'center' });
    doc.setFontSize(9);
    doc.text('Presidenta de NatTelf C.A.', pageWidth / 2, sigY + 10, { align: 'center' });
    
    doc.setFontSize(8);
    doc.setTextColor(150);
    doc.text(`Validación Electrónica: NT-PRES-${employee.dni}-${Date.now()}`, pageWidth / 2, sigY + 20, { align: 'center' });
    
    doc.save(`Constancia_Trabajo_${employee.dni}.pdf`);
    
    // Log
    await api.post('audit-logs/create_manual/', {
        action: 'other',
        module: 'RRHH',
        description: `Exportación de Constancia de Trabajo: ${employee.first_name} ${employee.last_name}`
    });
};

/**
 * Generates an Individual Pay Stub (Recibo de Pago Individual)
 */
export const generatePayStub = async (pay, employee) => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const logo = await loadImage('/logo.png');
    const signature = await loadImage('/signature.png');

    // Letterhead
    doc.setFillColor(149, 117, 205);
    doc.rect(10, 10, 5, 20, 'F');
    
    if (logo) {
        doc.addImage(logo, 'PNG', pageWidth - 35, 10, 25, 25);
    }
    
    doc.setTextColor(40);
    doc.setFontSize(18);
    doc.text('NatTelf', 20, 20);
    doc.setFontSize(10);
    doc.text('RECIBO DE PAGO DE NÓMINA', 20, 28);
    
    // Employee / Period Info
    doc.rect(10, 40, pageWidth - 20, 30);
    doc.text(`Empleado: ${employee.first_name} ${employee.last_name}`, 15, 48);
    doc.text(`Cédula: ${employee.dni}`, 15, 56);
    doc.text(`Cargo: ${employee.position}`, 15, 64);
    doc.text(`Periodo: ${pay.period_month}/${pay.period_year}`, 140, 48);
    doc.text(`Fecha Pago: ${pay.payment_date || 'PENDIENTE'}`, 140, 56);
    
    // Table
    autoTable(doc, {
        startY: 80,
        head: [['CONCEPTO', 'ASIGNACIONES', 'DEDUCCIONES']],
        body: [
            ['Sueldo Base', `$${pay.base_salary}`, ''],
            ['Cesta Ticket', `$${pay.food_stamps}`, ''],
            ['Bonificaciones', `$${pay.bonuses}`, ''],
            ['Retenciones / Deducciones', '', `$${pay.deductions}`],
            [{ content: 'TOTAL NETO A PAGAR', styles: { fontStyle: 'bold' } }, { content: `$${pay.net_salary}`, colSpan: 2, styles: { halign: 'right', fontStyle: 'bold' } }]
        ],
        theme: 'grid',
        headStyles: { fillColor: [149, 117, 205] }
    });
    
    // Footer / Signatures
    const finalY = doc.lastAutoTable.finalY + 40;
    
    // Admin signature placeholder
    if (signature) {
        doc.addImage(signature, 'PNG', 135, finalY - 25, 40, 15);
    }
    
    doc.line(30, finalY, 80, finalY);
    doc.text('Firma Empleado', 40, finalY + 5);
    doc.line(130, finalY, 180, finalY);
    doc.text('Nathaliee Vargas', 140, finalY + 5);
    doc.setFontSize(8);
    doc.text('Presidencia NatTelf', 142, finalY + 9);
    
    doc.setFontSize(8);
    doc.setTextColor(180);
    doc.text(`VALIDACIÓN DIGITAL: NT-PAY-${pay.id}-${Date.now()}`, pageWidth / 2, finalY + 20, { align: 'center' });
    
    doc.save(`Recibo_Pago_${employee.dni}_${pay.period_month}_${pay.period_year}.pdf`);
    
    // Log
    await api.post('audit-logs/create_manual/', {
        action: 'other',
        module: 'Nómina',
        description: `Exportación de Recibo de Pago: ${employee.first_name} ${employee.last_name} (${pay.period_month}/${pay.period_year})`
    });
};
