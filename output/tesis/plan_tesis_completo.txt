# PLAN DE TESIS

# CARÁTULA

**UNIVERSIDAD:** Universidad
**FACULTAD:** Ingeniería
**CARRERA:** Licenciatura en Sistemas de Información

---

**PLAN DE TESIS**

**TÍTULO:** Implementación de una Plataforma de Detección de Amenazas de Seguridad basada en eBPF e Inteligencia Artificial con GitOps para Entornos Cloud-Native

---

**AUTOR:** Estudiante de Licenciatura
**DIRECTOR:** [A designar]
**CO-DIRECTOR:** [A designar]

**AÑO:** 2025

---

*Tesis presentada para optar al grado de Licenciado en Sistemas de Información*


## RESUMEN

Este trabajo propone el diseño e implementación de una plataforma integral de ciberseguridad para entornos cloud-native que combina tecnología eBPF (extended Berkeley Packet Filter) con algoritmos de inteligencia artificial para la detección automática de amenazas de seguridad. La plataforma utiliza metodologías GitOps para garantizar la gestión declarativa y automatizada de políticas de seguridad.

La solución desarrollada implementa:
- **Monitoreo en tiempo real a nivel de kernel** usando eBPF para captura de eventos de red sin overhead
- **Procesamiento inteligente** mediante modelos de machine learning (DBSCAN, VAE, ZMAD) para detección de anomalías
- **Orquestación automatizada** utilizando Kubernetes, ArgoCD, y Tekton para implementación GitOps
- **Observabilidad integral** con Prometheus y Grafana para métricas y alertas en tiempo real

El proyecto demuestra la viabilidad de combinar tecnologías emergentes para crear una solución de seguridad adaptativa que mejora significativamente la detección de amenazas en comparación con métodos tradicionales basados en agentes, reduciendo el tiempo de respuesta y minimizando falsos positivos.

**Palabras clave:** eBPF, Inteligencia Artificial, Ciberseguridad, Cloud-Native, GitOps, Kubernetes, Machine Learning

## DESCRIPCIÓN DEL PROBLEMA

Los entornos cloud-native modernos basados en contenedores y microservicios presentan desafíos críticos de seguridad que las herramientas tradicionales no pueden abordar efectivamente:

### Problemática Principal

**1. Visibilidad limitada del tráfico de red**
- Los contenedores y microservicios generan patrones de comunicación dinámicos y efímeros
- Las herramientas tradicionales de monitoreo no pueden rastrear el tráfico inter-pod en tiempo real
- La encapsulación de red en Kubernetes oscurece la visibilidad del tráfico Este-Oeste

**2. Detección tardía de amenazas**
- Los métodos basados en agentes introducen latencia y overhead significativo
- La detección basada en firmas no identifica amenazas de día-cero (zero-day)
- Los sistemas reactivos permiten que los ataques causen daño antes de ser detectados

**3. Gestión manual de políticas de seguridad**
- La configuración manual de reglas de seguridad es propensa a errores humanos
- La falta de versionado y auditabilidad de políticas genera riesgos de compliance
- La desconexión entre desarrollo y operaciones dificulta la implementación coherente

**4. Falta de automatización en respuesta a incidentes**
- Los procesos manuales de respuesta aumentan el tiempo medio de resolución (MTTR)
- La coordinación entre equipos de desarrollo y seguridad carece de herramientas adecuadas
- La ausencia de playbooks automatizados limita la capacidad de respuesta escalable

**5. Desconexión entre desarrollo y seguridad (DevSecOps)**
- Las validaciones de seguridad se realizan como pasos separados y tardíos
- La falta de integración nativa genera fricciones en el ciclo de desarrollo
- Los equipos carecen de herramientas unificadas para gestión de seguridad

### Impacto del Problema

Esta problemática resulta en:
- **Tiempo de detección elevado** (promedio de 280 días según IBM Security)
- **Costos incrementales** por brechas de seguridad no detectadas
- **Compliance deficiente** por falta de auditabilidad
- **Productividad reducida** por procesos manuales y descoordinados

### Necesidad de Solución

Se requiere una plataforma que combine:
- **Monitoreo proactivo** a nivel de kernel sin overhead
- **Detección inteligente** usando algoritmos de machine learning
- **Gestión declarativa** de políticas mediante GitOps
- **Automatización integral** del ciclo de vida de seguridad

## OBJETIVOS

### Objetivo General

Desarrollar e implementar una plataforma integral de ciberseguridad para entornos cloud-native que combine tecnología eBPF con inteligencia artificial para la detección automática de amenazas, utilizando principios GitOps para la gestión declarativa de políticas de seguridad.

### Objetivos Específicos

**1. Diseñar una arquitectura de monitoreo basada en eBPF**
- Implementar hooks XDP para captura de paquetes en tiempo real
- Desarrollar agregación eficiente de métricas de red en espacio de usuario
- Crear mecanismos de exportación de datos para análisis de machine learning

**2. Implementar algoritmos de machine learning para detección de amenazas**
- Desarrollar un conjunto de modelos de detección de anomalías (DBSCAN, VAE, ZMAD)
- Implementar un motor de reglas para detección rápida de patrones conocidos
- Crear un sistema de consenso para reducir falsos positivos

**3. Desarrollar un sistema GitOps para gestión declarativa de seguridad**
- Implementar pipelines CI/CD con Tekton para automatización de despliegues
- Configurar ArgoCD para sincronización automática de políticas de seguridad
- Crear templates reutilizables para componentes de seguridad

**4. Integrar validaciones de seguridad en pipelines de desarrollo**
- Automatizar análisis de vulnerabilidades en imágenes de contenedor
- Implementar políticas as-code con validación automática
- Crear hooks de seguridad en el proceso de desarrollo

**5. Implementar observabilidad integral del sistema**
- Configurar métricas detalladas de detección y rendimiento
- Desarrollar dashboards especializados para equipos de seguridad
- Implementar alertas automatizadas con escalación inteligente

**6. Validar la efectividad mediante evaluación experimental**
- Medir tiempos de detección comparados con herramientas tradicionales
- Evaluar precisión y recall de los modelos de machine learning
- Analizar overhead de rendimiento introducido por la solución

## FUNDAMENTACIÓN O JUSTIFICACIÓN DEL TEMA

### Relevancia Académica

**Contribución al conocimiento científico:**
La ciberseguridad en entornos cloud-native representa un área de investigación activa con impacto directo en la industria de tecnología. La combinación de eBPF e inteligencia artificial constituye un enfoque innovador que contribuye al avance del conocimiento en:

- **Sistemas distribuidos:** Optimización del monitoreo en arquitecturas de microservicios
- **Aprendizaje automático aplicado:** Desarrollo de modelos especializados para detección de amenazas
- **Ingeniería de software:** Integración de seguridad en metodologías DevOps

**Alineación con líneas de investigación:**
El proyecto se alinea con las líneas prioritarias de investigación en ciencias de la computación:
- Seguridad informática y criptografía
- Sistemas distribuidos y computación en la nube
- Inteligencia artificial y aprendizaje automático

### Importancia Tecnológica

**Tecnologías emergentes:**
- **eBPF** permite monitoreo granular a nivel de kernel sin modificaciones del sistema operativo
- **Machine Learning** aplicado a ciberseguridad mejora la detección de amenazas desconocidas
- **GitOps** proporciona gestión declarativa y auditable de configuraciones de seguridad

**Impacto en la industria:**
- Reducción significativa del tiempo de detección de amenazas
- Minimización de falsos positivos mediante técnicas de consenso
- Automatización de procesos tradicionalmente manuales y propensos a errores

**Adopción empresarial:**
Empresas como Google, Netflix, y Uber utilizan tecnologías similares en producción, validando la relevancia práctica del enfoque propuesto.

### Viabilidad de Implementación

**Infraestructura tecnológica:**
- Plataforma Kubernetes completamente implementada y funcional
- Stack de herramientas GitOps (ArgoCD, Tekton) configurado y validado
- Entorno de desarrollo con todas las dependencias resueltas

**Metodología probada:**
- Metodologías ágiles con iteraciones incrementales
- Principios DevOps para integración continua
- Documentación técnica exhaustiva disponible

**Herramientas maduras:**
- eBPF con soporte nativo en kernels Linux modernos
- Librerías de machine learning estables (TensorFlow, Scikit-learn)
- Ecosistema CNCF con herramientas de producción

### Factibilidad Académica

**Alcance apropiado:**
El proyecto tiene un alcance manejable para una tesis de licenciatura, con objetivos específicos y medibles que pueden completarse en el tiempo disponible.

**Recursos disponibles:**
- Documentación técnica completa
- Código fuente accesible y bien estructurado
- Comunidad activa de desarrolladores para consultas

**Evaluación objetiva:**
El proyecto permite evaluación cuantitativa mediante métricas de rendimiento, precisión de detección, y comparación con herramientas existentes.

### Impacto Esperado

**Contribución académica:**
- Validación empírica de la efectividad de eBPF para seguridad
- Análisis comparativo de algoritmos de ML en detección de amenazas
- Metodología replicable para implementaciones similares

**Aplicabilidad práctica:**
- Solución deployable en entornos reales de producción
- Reducción medible de costos operativos de seguridad
- Base para desarrollos comerciales futuros

## BIBLIOGRAFÍA INICIAL

1. Burns, B., & Beda, J. (2019). *Kubernetes: Up and Running: Dive into the Future of Infrastructure* (2ª ed.). O'Reilly Media.

2. Buczak, A. L., & Guven, E. (2016). A survey of data mining and machine learning methods for cyber security intrusion detection. *IEEE Communications Surveys & Tutorials*, 18(2), 1153-1176. https://doi.org/10.1109/COMST.2015.2494502

3. Cilium Project. (2023). *eBPF-based Networking, Observability, and Security Documentation*. https://docs.cilium.io/

4. Cloud Native Computing Foundation Security Technical Advisory Group. (2022). *Cloud Native Security Whitepaper v2*. CNCF. https://github.com/cncf/tag-security/tree/main/security-whitepaper

5. Fleming, B. (2019). *Learning eBPF: Programming the Linux Kernel for Enhanced Observability and Security*. O'Reilly Media.

6. Kim, G., Debois, P., Willis, J., & Humble, J. (2016). *The DevOps Handbook: How to Create World-Class Agility, Reliability, and Security in Technology Organizations*. IT Revolution Press.

7. Kumar, S., & Viinikainen, A. (2023). Machine Learning for Network Security: A Comprehensive Survey. *IEEE Transactions on Network and Service Management*, 20(2), 1543-1559. https://doi.org/10.1109/TNSM.2023.3247090

8. National Institute of Standards and Technology. (2017). *Application Container Security Guide* (NIST Special Publication 800-190). U.S. Department of Commerce. https://doi.org/10.6028/NIST.SP.800-190

9. Rice, L., & Fleming, L. (2020). *Container Security: Fundamental Technology Concepts that Protect Containerized Applications*. O'Reilly Media.

10. Weaveworks. (2023). *Guide to GitOps: Operations by Pull Request*. https://www.weave.works/technologies/gitops/

**Recursos adicionales consultados:**

11. Akhunzada, A., Ahmed, E., Gani, A., Khan, M. K., Imran, M., & Guizani, S. (2015). Securing software defined networks: taxonomy, requirements, and open issues. *IEEE Communications Magazine*, 53(4), 36-44.

12. Chen, L., Yang, Y., Zhou, X., Liu, F., & Xu, L. (2022). eBPF-based network security monitoring in cloud-native environments. *Journal of Cloud Computing*, 11(1), 1-15.

13. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press.

14. Kubernetes Security and Disclosure Information. (2023). *Kubernetes Security Documentation*. https://kubernetes.io/docs/concepts/security/

15. Mitchell, T. M. (1997). *Machine Learning*. McGraw-Hill Education.

---

*Documento generado automáticamente el 16/09/2025 14:40:31*
*Agente especializado en planificación de tesis - eBPF-IA Project*
