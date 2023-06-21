<#--  =====================
      MACRO mhc_process_pios
      ===================== -->
<#compress>
<#macro mhc_process_pios>
    <#assign pioOutList = []>
    <#assign pioInList = []>
    <#list 1..core.PIO_PIN_TOTAL as i>
        <#assign funcType = "core.PIN_" + i + "_FUNCTION_TYPE">
        <#assign funcName = "core.PIN_" + i + "_FUNCTION_NAME">
        <#assign pinPos = "core.PIN_" + i + "_PIO_PIN">
        <#assign pinChannel = "core.PIN_" + i + "_PIO_CHANNEL">
        <#assign pinDir = "core.PIN_" + i + "_DIR">
        <#assign pinLat = "core.PIN_" + i + "_LAT">
        <#assign pinPu = "core.PIN_" + i + "_PU">
        <#if funcType?eval?has_content>
            <#if (funcType?eval == "GPIO")>
                <#if funcName?eval?has_content>
                    <#if pinPos?eval?has_content>
                        <#if pinChannel?eval?has_content>
                            <#assign sublist = []>
                            <#assign sublist = sublist + [funcName?eval]>
                            <#assign sublist = sublist + [pinPos?eval]>
                            <#assign sublist = sublist + [pinChannel?eval]>
                            <#if pinDir?eval?has_content && pinDir?eval == "Out">
                                <#if pinLat?eval?has_content>
                                    <#assign sublist = sublist + [pinLat?eval]>
                                </#if>
                                <#assign pioOutList = pioOutList + [sublist]>
                            <#else>
                                <#if pinPu?eval?has_content>
                                    <#assign sublist = sublist + [pinPu?eval]>
                                <#else>
                                    <#assign sublist = sublist + ["False"]>
                                </#if>
                                <#assign pioInList = pioInList + [sublist]>
                            </#if>
                        </#if>
                    </#if>
                </#if>
            </#if>
        </#if>
    </#list>
</#macro>

<#--  =====================
      MACRO execution
      ===================== -->
<@mhc_process_pios/>
</#compress>
<#if (pioOutList?size > 0)>
    <#list pioOutList as pin>
        <#assign name = pin[0]>
        <#assign pos = pin[1]>
        <#assign chn = pin[2]>
        <#assign latch = pin[3]>

        <#lt>/*** OUTPUT PIO Macros for ${name} ***/
        <#lt>#define BSP_${name}_PIN          PIO_PIN_P${chn}${pos}
        <#lt>#define BSP_${name}_Get()        ((PIO${chn}_REGS->PIO_PDSR >> ${pos}) & 0x1)
        <#if latch == "High">
            <#lt>#define BSP_${name}_On()         (PIO${chn}_REGS->PIO_CODR = (1UL<<${pos}))
            <#lt>#define BSP_${name}_Off()        (PIO${chn}_REGS->PIO_SODR = (1UL<<${pos}))
        <#else>
            <#lt>#define BSP_${name}_On()         (PIO${chn}_REGS->PIO_SODR = (1UL<<${pos}))
            <#lt>#define BSP_${name}_Off()        (PIO${chn}_REGS->PIO_CODR = (1UL<<${pos}))
        </#if>
        <#lt>#define BSP_${name}_Toggle()     do {\
        <#lt>                                   PIO${chn}_REGS->PIO_MSKR = (1<<${pos}); \
        <#lt>                                   PIO${chn}_REGS->PIO_ODSR ^= (1<<${pos});\
        <#lt>                               } while (0)
    </#list>
</#if>
<#if (pioInList?size > 0)>
    <#list pioInList as pin>
        <#assign name = pin[0]>
        <#assign pos = pin[1]>
        <#assign chn = pin[2]>
        <#assign pu = pin[3]>

        <#lt>/*** INPUT PIO Macros for ${name} ***/
        <#lt>#define BSP_${name}_PIN                    PIO_PIN_P${chn}${pos}
        <#lt>#define BSP_${name}_Get()                  ((PIO${chn}_REGS->PIO_PDSR >> ${pos}) & 0x1)
        <#if pu == "True">    
            <#lt>#define BSP_${name}_STATE_PRESSED          0
            <#lt>#define BSP_${name}_STATE_RELEASED         1
        <#else>    
            <#lt>#define BSP_${name}_STATE_PRESSED          1
            <#lt>#define BSP_${name}_STATE_RELEASED         0
        </#if>    
        <#lt>#define BSP_${name}_InterruptEnable()      (PIO${chn}_REGS->PIO_IER = (1<<${pos}))
        <#lt>#define BSP_${name}_InterruptDisable()     (PIO${chn}_REGS->PIO_IDR = (1<<${pos}))
    </#list>
</#if>
<#--
/*******************************************************************************
 End of File
*/
-->
