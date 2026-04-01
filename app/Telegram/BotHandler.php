<?php

namespace App\Telegram;

use App\Telegram\Handlers\Admin\AdminMenuHandler;
use App\Telegram\Handlers\Admin\LogCategoryHandler;
use App\Telegram\Handlers\Admin\RecipeAdminHandler;
use App\Telegram\Handlers\Admin\RecipeCategoryHandler;
use App\Telegram\Handlers\Admin\ReminderAdminHandler;
use App\Telegram\Handlers\LogEntryHandler;
use App\Telegram\Handlers\RecipeHandler;
use App\Telegram\Handlers\ReminderHandler;
use App\Telegram\Handlers\StartHandler;
use Illuminate\Support\Facades\Log;
use Telegram\Bot\Objects\Update;

class BotHandler
{
    public function __construct(
        private ConversationManager  $conv,
        private StartHandler         $start,
        private ReminderHandler      $reminders,
        private RecipeHandler        $recipes,
        private LogEntryHandler      $logEntry,
        private AdminMenuHandler     $adminMenu,
        private ReminderAdminHandler $reminderAdmin,
        private LogCategoryHandler   $logCategory,
        private RecipeCategoryHandler $recipeCategory,
        private RecipeAdminHandler   $recipeAdmin,
    ) {}

    public function handle(Update $update): void
    {
        $userId = $update->getMessage()?->getFrom()?->getId()
                  ?? $update->getCallbackQuery()?->getFrom()?->getId();

        if (!$userId) {
            return;
        }

        // 1. Commands
        if ($text = $update->getMessage()?->getText()) {
            if (str_starts_with($text, '/start')) {
                $this->start->handleCommand($update);
                return;
            }
            if (str_starts_with($text, '/cancel')) {
                $this->conv->clearState($userId);
                return;
            }
        }

        // 2. Active conversation state (text message mid-flow)
        $state = $this->conv->getState($userId);
        if ($update->getMessage() && $state) {
            match ($state) {
                'log:enter_subject'   => $this->logEntry->handleSubject($update),
                'log:enter_message'   => $this->logEntry->handleMessage($update),
                'arem:enter_message'  => $this->reminderAdmin->handleMessage($update),
                'arem:enter_cron'     => $this->reminderAdmin->handleCron($update),
                'arem:enter_channel'  => $this->reminderAdmin->handleChannel($update),
                'alcat:enter_name'    => $this->logCategory->handleName($update),
                'arcat:enter_name'    => $this->recipeCategory->handleName($update),
                'arec:enter_name'     => $this->recipeAdmin->handleName($update),
                'arec:enter_content'  => $this->recipeAdmin->handleContent($update),
                default               => Log::debug("Unhandled conversation state: {$state}"),
            };
            return;
        }

        // 3. Callback queries
        if ($cbq = $update->getCallbackQuery()) {
            $data = $cbq->getData();
            $this->routeCallback($update, $data, $userId);
        }
    }

    private function routeCallback(Update $update, string $data, int $userId): void
    {
        match (true) {
            $data === 'main:menu'                         => $this->start->handleMainMenu($update),
            $data === 'view:reminders'                    => $this->reminders->handleView($update),
            $data === 'recipe:categories'                 => $this->recipes->handleCategories($update),
            str_starts_with($data, 'recipe:list:')        => $this->recipes->handleList($update, (int) substr($data, 12)),
            str_starts_with($data, 'recipe:view:')        => $this->recipes->handleView($update, (int) substr($data, 12)),
            $data === 'log:start'                         => $this->logEntry->handleStart($update),
            str_starts_with($data, 'log:cat:')            => $this->logEntry->handleCategorySelect($update, (int) substr($data, 8)),
            $data === 'admin:menu'                        => $this->adminMenu->handle($update),
            $data === 'admin:rem:menu'                    => $this->reminderAdmin->handleMenu($update),
            $data === 'admin:rem:add'                     => $this->reminderAdmin->handleAddStart($update),
            str_starts_with($data, 'admin:rem:del:')      => $this->reminderAdmin->handleDelete($update, (int) substr($data, 14)),
            $data === 'admin:lcat:menu'                   => $this->logCategory->handleMenu($update),
            $data === 'admin:lcat:add'                    => $this->logCategory->handleAddStart($update),
            $data === 'admin:rcat:menu'                   => $this->recipeCategory->handleMenu($update),
            $data === 'admin:rcat:add'                    => $this->recipeCategory->handleAddStart($update),
            $data === 'admin:rec:add'                     => $this->recipeAdmin->handleAddStart($update),
            str_starts_with($data, 'admin:rec:cat:')      => $this->recipeAdmin->handleCatSelect($update, (int) substr($data, 14)),
            $data === 'noop'                              => null,
            default                                       => Log::debug("Unhandled callback: {$data}"),
        };
    }
}
